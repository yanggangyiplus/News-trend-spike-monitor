"""
FastAPI 메인 애플리케이션
RESTful API 엔드포인트 제공
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Query, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import logging
import time

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.services.trend_service import TrendService
from src.services.monitoring import metrics_collector, monitor_api_response
from app.api.cache import cache
from app.api.job_queue import job_queue, JobStatus

# 로거 설정
logger = setup_logger("api", level=logging.INFO)

# FastAPI 앱 초기화
app = FastAPI(
    title="News Trend Spike Monitor API",
    description="뉴스 기반 실시간 트렌드 스파이크 모니터링 API",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 서비스 인스턴스
trend_service: Optional[TrendService] = None

# Throttling을 위한 마지막 호출 시간 저장
_last_latest_call: float = 0.0


# Pydantic 모델 정의
class AnalyzeRequest(BaseModel):
    """분석 요청 모델"""
    keyword: str = Field(..., description="분석할 키워드", min_length=1, max_length=100)
    max_results: int = Field(100, ge=1, le=1000, description="최대 수집 뉴스 개수")
    time_window_hours: int = Field(24, ge=1, le=168, description="시간 윈도우 (시간)")


class AnalyzeResponse(BaseModel):
    """분석 응답 모델"""
    keyword: str
    total_news: int
    avg_sentiment: float
    time_series: List[Dict]
    spikes: List[Dict]
    anomalies: Dict[str, List[Dict]]
    news_items: List[Dict]
    analyzed_at: str


class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    service: str
    timestamp: str


class LatestResponse(BaseModel):
    """최근 데이터 응답 모델"""
    keyword: Optional[str] = None
    items: List[Dict]
    count: int
    hours: int


class SpikesResponse(BaseModel):
    """스파이크 응답 모델"""
    spikes: List[Dict]
    count: int
    limit: int


class JobResponse(BaseModel):
    """작업 응답 모델"""
    job_id: str
    status: str
    message: str


class JobResultResponse(BaseModel):
    """작업 결과 응답 모델"""
    job_id: str
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    global trend_service
    
    try:
        # 설정 파일 로드
        config = load_config("configs/config_api.yaml")
        
        # 서비스 초기화
        trend_service = TrendService(config_path="configs/config_api.yaml")
        
        # 캐시 정리 작업 시작
        import asyncio
        asyncio.create_task(periodic_cache_cleanup())
        
        # 모델 warm-up 수행
        try:
            if trend_service and trend_service.sentiment_analyzer:
                trend_service.sentiment_analyzer.warm_up()
        except Exception as e:
            logger.warning(f"모델 warm-up 실패: {e}")
        
        # 주기적 작업 큐 정리
        asyncio.create_task(periodic_job_cleanup())
        
        logger.info("FastAPI 서버 시작 완료")
    
    except Exception as e:
        logger.error(f"서버 초기화 오류: {e}")
        # 기본 설정으로 폴백
        trend_service = TrendService()


async def periodic_cache_cleanup():
    """주기적 캐시 정리 작업"""
    import asyncio
    while True:
        try:
            await asyncio.sleep(300)  # 5분마다
            cache.cleanup_expired()
        except Exception as e:
            logger.error(f"캐시 정리 오류: {e}")
            await asyncio.sleep(60)  # 오류 시 1분 대기


async def periodic_job_cleanup():
    """주기적 작업 큐 정리"""
    import asyncio
    while True:
        try:
            await asyncio.sleep(3600)  # 1시간마다
            job_queue.cleanup_old_jobs(max_age_hours=24)
        except Exception as e:
            logger.error(f"작업 큐 정리 오류: {e}")
            await asyncio.sleep(300)


def analyze_trend_background(
    keyword: str,
    max_results: int,
    time_window_hours: int,
):
    """백그라운드에서 트렌드 분석 수행"""
    try:
        result = trend_service.analyze_trend(
            keyword=keyword,
            max_results=max_results,
            time_window_hours=time_window_hours,
        )
        # 결과를 캐시에 저장
        cache.set("analyze", result, ttl=600, keyword=keyword, max_results=max_results, time_window_hours=time_window_hours)
        logger.info(f"백그라운드 분석 완료: {keyword}")
    except Exception as e:
        logger.error(f"백그라운드 분석 오류: {e}")


@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "News Trend Spike Monitor API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@monitor_api_response("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    
    Returns:
        서비스 상태 정보
    """
    return HealthResponse(
        status="healthy",
        service="news-trend-monitor",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """
    Prometheus 포맷 메트릭 엔드포인트
    
    Returns:
        Prometheus 포맷 메트릭
    """
    from fastapi.responses import PlainTextResponse
    metrics = metrics_collector.get_prometheus_metrics()
    return PlainTextResponse(content=metrics, media_type="text/plain")


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
@monitor_api_response("/analyze")
async def analyze_trend(
    request: AnalyzeRequest = Body(...),
    background_tasks: BackgroundTasks = None,
):
    """
    키워드 트렌드 분석 (캐싱 적용)
    
    Args:
        request: 분석 요청 (키워드, 최대 결과 수, 시간 윈도우)
        background_tasks: 백그라운드 작업
        
    Returns:
        분석 결과
    """
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    # 캐시 확인
    cached_result = cache.get(
        "analyze",
        keyword=request.keyword,
        max_results=request.max_results,
        time_window_hours=request.time_window_hours,
    )
    
    if cached_result is not None:
        logger.info(f"캐시 히트: {request.keyword}")
        return AnalyzeResponse(**cached_result)
    
    try:
        # 백그라운드에서 분석 수행 (비동기)
        if background_tasks:
            background_tasks.add_task(
                analyze_trend_background,
                request.keyword,
                request.max_results,
                request.time_window_hours,
            )
        
        # 동기 분석 수행
        result = trend_service.analyze_trend(
            keyword=request.keyword,
            max_results=request.max_results,
            time_window_hours=request.time_window_hours,
        )
        
        # 결과 캐싱
        cache.set(
            "analyze",
            result,
            ttl=600,
            keyword=request.keyword,
            max_results=request.max_results,
            time_window_hours=request.time_window_hours,
        )
        
        return AnalyzeResponse(**result)
    
    except Exception as e:
        logger.error(f"분석 오류: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@app.get("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
@monitor_api_response("/analyze")
async def analyze_trend_get(
    keyword: str = Query(..., description="분석할 키워드", min_length=1, max_length=100),
    max_results: int = Query(100, ge=1, le=1000, description="최대 수집 뉴스 개수"),
    time_window_hours: int = Query(24, ge=1, le=168, description="시간 윈도우 (시간)"),
    background_tasks: BackgroundTasks = None,
):
    """
    키워드 트렌드 분석 (GET 방식, 캐싱 적용)
    
    Args:
        keyword: 분석할 키워드
        max_results: 최대 수집 뉴스 개수
        time_window_hours: 시간 윈도우
        background_tasks: 백그라운드 작업
        
    Returns:
        분석 결과
    """
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    # 캐시 확인
    cached_result = cache.get(
        "analyze",
        keyword=keyword,
        max_results=max_results,
        time_window_hours=time_window_hours,
    )
    
    if cached_result is not None:
        logger.info(f"캐시 히트: {keyword}")
        return AnalyzeResponse(**cached_result)
    
    try:
        # 백그라운드에서 분석 수행
        if background_tasks:
            background_tasks.add_task(
                analyze_trend_background,
                keyword,
                max_results,
                time_window_hours,
            )
        
        result = trend_service.analyze_trend(
            keyword=keyword,
            max_results=max_results,
            time_window_hours=time_window_hours,
        )
        
        # 결과 캐싱
        cache.set(
            "analyze",
            result,
            ttl=600,
            keyword=keyword,
            max_results=max_results,
            time_window_hours=time_window_hours,
        )
        
        return AnalyzeResponse(**result)
    
    except Exception as e:
        logger.error(f"분석 오류: {e}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@app.get("/latest", response_model=LatestResponse, tags=["Data"])
async def get_latest(
    hours: int = Query(1, ge=1, le=24, description="조회할 시간 범위"),
):
    """
    최근 N시간 데이터 조회 (Throttling 적용: 1초 간격)
    
    Args:
        hours: 조회할 시간 범위 (기본값: 1시간)
        
    Returns:
        최근 뉴스 데이터
    """
    global _last_latest_call
    
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    # Throttling: 1초 간격으로만 갱신
    current_time = time.time()
    if current_time - _last_latest_call < 1.0:
        # 캐시된 결과 반환
        cached_result = cache.get("latest", hours=hours)
        if cached_result:
            return LatestResponse(**cached_result)
    
    _last_latest_call = current_time
    
    try:
        items = trend_service.get_latest_data(hours=hours)
        
        result = LatestResponse(
            items=items,
            count=len(items),
            hours=hours,
        )
        
        # 결과 캐싱 (1초 TTL)
        cache.set("latest", result.dict(), ttl=1, hours=hours)
        
        return result
    
    except Exception as e:
        logger.error(f"최근 데이터 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")


@app.get("/spikes", response_model=SpikesResponse, tags=["Spikes"])
async def get_spikes(
    limit: int = Query(10, ge=1, le=100, description="최대 개수"),
):
    """
    최근 스파이크 목록 조회
    
    Args:
        limit: 최대 개수 (기본값: 10)
        
    Returns:
        스파이크 목록
    """
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    try:
        spikes = trend_service.get_recent_spikes(limit=limit)
        
        return SpikesResponse(
            spikes=spikes,
            count=len(spikes),
            limit=limit,
        )
    
    except Exception as e:
        logger.error(f"스파이크 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"스파이크 조회 중 오류 발생: {str(e)}")


@app.post("/analyze/async", response_model=JobResponse, tags=["Analysis"])
@monitor_api_response("/analyze/async")
async def analyze_trend_async(request: AnalyzeRequest = Body(...)):
    """
    비동기 키워드 트렌드 분석 (Background Job)
    
    Args:
        request: 분석 요청
        
    Returns:
        작업 ID 및 상태
    """
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    # 작업 생성
    job_id = job_queue.create_job(
        job_type="analyze_trend",
        params={
            "keyword": request.keyword,
            "max_results": request.max_results,
            "time_window_hours": request.time_window_hours,
        }
    )
    
    # 백그라운드 작업 실행
    import asyncio
    asyncio.create_task(process_analyze_job(job_id, request))
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="분석 작업이 시작되었습니다. /result/{job_id}로 결과를 확인하세요.",
    )


async def process_analyze_job(job_id: str, request: AnalyzeRequest):
    """분석 작업 처리"""
    job_queue.update_job_status(job_id, JobStatus.PROCESSING)
    
    try:
        result = trend_service.analyze_trend(
            keyword=request.keyword,
            max_results=request.max_results,
            time_window_hours=request.time_window_hours,
        )
        
        job_queue.update_job_status(job_id, JobStatus.COMPLETED, result=result)
        logger.info(f"작업 완료: {job_id}")
    
    except Exception as e:
        job_queue.update_job_status(job_id, JobStatus.FAILED, error=str(e))
        logger.error(f"작업 실패: {job_id} - {e}")


@app.get("/result/{job_id}", response_model=JobResultResponse, tags=["Analysis"])
@monitor_api_response("/result")
async def get_job_result(job_id: str):
    """
    작업 결과 조회
    
    Args:
        job_id: 작업 ID
        
    Returns:
        작업 결과
    """
    job = job_queue.get_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return JobResultResponse(**job)


@app.get("/sentiment", tags=["Analysis"])
@monitor_api_response("/sentiment")
async def analyze_sentiment(
    text: str = Query(..., description="분석할 텍스트", min_length=1),
):
    """
    텍스트 감정 분석
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        감정 분석 결과
    """
    if trend_service is None:
        raise HTTPException(status_code=503, detail="서비스가 초기화되지 않았습니다")
    
    try:
        sentiment = trend_service.sentiment_analyzer.analyze(text)
        return {
            "text": text,
            "sentiment": sentiment,
            "score": sentiment.get("positive", 0.5),
            "confidence": sentiment.get("confidence", 0.0),
        }
    
    except Exception as e:
        logger.error(f"감정 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=f"감정 분석 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run(app, host="0.0.0.0", port=8000)
