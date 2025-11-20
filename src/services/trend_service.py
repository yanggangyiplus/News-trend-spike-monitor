"""
트렌드 분석 서비스
데이터 수집부터 감정 분석, 스파이크 감지까지 통합 서비스
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

from src.data.rss_collector import RSSCollector
from src.data.google_news_collector import GoogleNewsCollector
from src.data.text_cleaner import TextCleaner
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.anomaly.zscore_detector import ZScoreDetector
from src.anomaly.moving_average_detector import MovingAverageDetector
from src.anomaly.spike_detector import SpikeDetector

logger = logging.getLogger(__name__)


class TrendService:
    """트렌드 분석 서비스 클래스"""
    
    def __init__(
        self,
        rss_urls: Optional[List[str]] = None,
        google_news_api_key: Optional[str] = None,
        sentiment_model: str = "beomi/KcELECTRA-base",
        config_path: Optional[str] = None,
    ):
        """
        트렌드 분석 서비스 초기화
        
        Args:
            rss_urls: RSS 피드 URL 리스트
            google_news_api_key: Google News API 키
            sentiment_model: 감정 분석 모델 이름
            config_path: 설정 파일 경로
        """
        # 설정 파일 로드
        if config_path:
            try:
                from src.utils.config import load_config
                config = load_config(config_path)
                collector_config = config.get("collector", {})
                rss_urls = collector_config.get("rss_urls", rss_urls or [])
                google_news_config = collector_config.get("google_news", {})
                google_news_api_key = google_news_config.get("api_key", google_news_api_key)
                
                nlp_config = config.get("nlp", {})
                sentiment_model = nlp_config.get("model_name", sentiment_model)
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
        
        # 수집기 초기화
        self.rss_collector = RSSCollector(rss_urls=rss_urls, config_path=config_path)
        self.google_collector = GoogleNewsCollector(api_key=google_news_api_key, config_path=config_path)
        
        # 전처리기 초기화
        self.text_cleaner = TextCleaner()
        
        # 감정 분석기 초기화
        self.sentiment_analyzer = SentimentAnalyzer(model_name=sentiment_model)
        
        # 이상치/스파이크 감지기 초기화
        self.zscore_detector = ZScoreDetector(threshold=2.0)
        self.moving_avg_detector = MovingAverageDetector(window_size=5, threshold=2.0)
        self.spike_detector = SpikeDetector(threshold=2.0)
        
        logger.info("트렌드 분석 서비스 초기화 완료")
    
    def analyze_trend(
        self,
        keyword: str,
        max_results: int = 100,
        time_window_hours: int = 24,
    ) -> Dict:
        """
        키워드 트렌드 분석 수행 (End-to-End 파이프라인)
        
        Args:
            keyword: 분석할 키워드
            max_results: 최대 수집 뉴스 개수
            time_window_hours: 분석 시간 윈도우 (시간)
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info(f"트렌드 분석 시작: {keyword}")
        
        # 1. 데이터 수집
        news_items = []
        
        # RSS 수집
        try:
            rss_items = self.rss_collector.collect(keyword=keyword, max_results=max_results)
            news_items.extend(rss_items)
            logger.info(f"RSS에서 {len(rss_items)}개 뉴스 수집")
        except Exception as e:
            logger.error(f"RSS 수집 오류: {e}")
        
        # Google News 수집
        try:
            google_items = self.google_collector.collect(keyword=keyword, max_results=max_results)
            news_items.extend(google_items)
            logger.info(f"Google News에서 {len(google_items)}개 뉴스 수집")
        except Exception as e:
            logger.error(f"Google News 수집 오류: {e}")
        
        if not news_items:
            logger.warning(f"수집된 뉴스가 없습니다: {keyword}")
            return self._empty_result(keyword)
        
        # 2. 전처리
        processed_items = []
        for item in news_items:
            # 텍스트 정제
            title = self.text_cleaner.clean_text(item.get("title", ""))
            summary = self.text_cleaner.clean_text(item.get("summary", ""))
            
            if not title and not summary:
                continue
            
            item["title_cleaned"] = title
            item["summary_cleaned"] = summary
            processed_items.append(item)
        
        # 중복 제거 (링크 기준)
        seen_links = set()
        unique_items = []
        for item in processed_items:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                unique_items.append(item)
        
        logger.info(f"전처리 완료: {len(unique_items)}개 고유 뉴스")
        
        # 3. 감정 분석
        sentiment_results = []
        for item in unique_items:
            text = f"{item.get('title_cleaned', '')} {item.get('summary_cleaned', '')}"
            
            if not text.strip():
                continue
            
            try:
                sentiment = self.sentiment_analyzer.analyze(text)
                sentiment_score = sentiment.get("positive", 0.5)
                confidence = sentiment.get("confidence", 0.0)
                
                item["sentiment"] = sentiment
                item["sentiment_score"] = sentiment_score
                item["confidence"] = confidence
                sentiment_results.append(sentiment_score)
            except Exception as e:
                logger.error(f"감정 분석 오류: {e}")
                item["sentiment_score"] = 0.5
                item["confidence"] = 0.0
        
        # 4. 시계열 데이터 생성
        time_series = self._create_time_series(unique_items, time_window_hours)
        
        if not time_series:
            logger.warning("시계열 데이터 생성 실패")
            return self._empty_result(keyword)
        
        # 5. 스파이크 감지
        df_time_series = pd.DataFrame(time_series)
        spikes = self.spike_detector.detect(df_time_series, column="avg_sentiment", return_details=True)
        
        # 6. 이상치 감지
        zscore_anomalies = self.zscore_detector.detect(df_time_series, column="avg_sentiment")
        moving_avg_anomalies = self.moving_avg_detector.detect(df_time_series, column="avg_sentiment")
        
        # 7. 결과 집계
        result = {
            "keyword": keyword,
            "total_news": len(unique_items),
            "avg_sentiment": float(np.mean(sentiment_results)) if sentiment_results else 0.5,
            "time_series": time_series,
            "spikes": spikes,
            "anomalies": {
                "zscore": zscore_anomalies,
                "moving_average": moving_avg_anomalies,
            },
            "news_items": unique_items[:20],  # 최신 20개만
            "analyzed_at": datetime.now().isoformat(),
        }
        
        logger.info(
            f"트렌드 분석 완료: {keyword} "
            f"({len(unique_items)}개 뉴스, {len(spikes)}개 스파이크)"
        )
        return result
    
    def _create_time_series(
        self,
        news_items: List[Dict],
        time_window_hours: int,
    ) -> List[Dict]:
        """
        시계열 데이터 생성 (시간별 기사 감정 평균)
        
        Args:
            news_items: 뉴스 아이템 리스트
            time_window_hours: 시간 윈도우
            
        Returns:
            시계열 데이터 리스트
        """
        if not news_items:
            return []
        
        # 데이터프레임 생성
        df = pd.DataFrame(news_items)
        
        # pubDate 파싱
        df["published_dt"] = pd.to_datetime(df["pubDate"], errors="coerce", format="%Y-%m-%d %H:%M:%S")
        df = df.dropna(subset=["published_dt", "sentiment_score"])
        
        if df.empty:
            return []
        
        # 시간 윈도우별 집계
        df["time_bin"] = df["published_dt"].dt.floor(f"{time_window_hours}H")
        
        grouped = df.groupby("time_bin").agg({
            "sentiment_score": ["mean", "count"],
            "confidence": "mean",
        }).reset_index()
        
        grouped.columns = ["timestamp", "avg_sentiment", "count", "avg_confidence"]
        
        time_series = []
        for _, row in grouped.iterrows():
            time_series.append({
                "timestamp": row["timestamp"].isoformat(),
                "avg_sentiment": float(row["avg_sentiment"]),
                "count": int(row["count"]),
                "avg_confidence": float(row["avg_confidence"]) if not pd.isna(row["avg_confidence"]) else 0.0,
            })
        
        return sorted(time_series, key=lambda x: x["timestamp"])
    
    def _empty_result(self, keyword: str) -> Dict:
        """빈 결과 반환"""
        return {
            "keyword": keyword,
            "total_news": 0,
            "avg_sentiment": 0.5,
            "time_series": [],
            "spikes": [],
            "anomalies": {
                "zscore": [],
                "moving_average": [],
            },
            "news_items": [],
            "analyzed_at": datetime.now().isoformat(),
        }
    
    def get_latest_data(self, hours: int = 1) -> List[Dict]:
        """
        최근 N시간 데이터 조회
        
        Args:
            hours: 조회할 시간 범위
            
        Returns:
            최근 뉴스 데이터 리스트
        """
        # 실제 구현에서는 데이터베이스나 캐시에서 조회
        # 현재는 빈 리스트 반환 (확장 가능)
        logger.info(f"최근 {hours}시간 데이터 조회")
        return []
    
    def get_recent_spikes(self, limit: int = 10) -> List[Dict]:
        """
        최근 스파이크 목록 조회
        
        Args:
            limit: 최대 개수
            
        Returns:
            스파이크 리스트
        """
        # 실제 구현에서는 데이터베이스나 캐시에서 조회
        # 현재는 빈 리스트 반환 (확장 가능)
        logger.info(f"최근 스파이크 {limit}개 조회")
        return []
