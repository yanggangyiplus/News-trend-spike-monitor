"""
백그라운드 작업 큐 모듈
NLP heavy 작업을 비동기로 처리
"""

import uuid
import asyncio
from typing import Dict, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """작업 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobQueue:
    """작업 큐 클래스"""
    
    def __init__(self):
        """작업 큐 초기화"""
        self.jobs: Dict[str, Dict] = {}
        logger.info("작업 큐 초기화 완료")
    
    def create_job(self, job_type: str, params: Dict) -> str:
        """
        작업 생성
        
        Args:
            job_type: 작업 타입
            params: 작업 파라미터
            
        Returns:
            작업 ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "job_type": job_type,
            "params": params,
            "status": JobStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None,
        }
        
        logger.info(f"작업 생성: {job_id} ({job_type})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        작업 조회
        
        Args:
            job_id: 작업 ID
            
        Returns:
            작업 정보 딕셔너리 또는 None
        """
        return self.jobs.get(job_id)
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """
        작업 상태 업데이트
        
        Args:
            job_id: 작업 ID
            status: 작업 상태
            result: 작업 결과
            error: 에러 메시지
        """
        if job_id not in self.jobs:
            logger.warning(f"존재하지 않는 작업: {job_id}")
            return
        
        self.jobs[job_id]["status"] = status
        self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        if result:
            self.jobs[job_id]["result"] = result
        
        if error:
            self.jobs[job_id]["error"] = error
        
        logger.info(f"작업 상태 업데이트: {job_id} -> {status}")
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        오래된 작업 정리
        
        Args:
            max_age_hours: 최대 보관 시간 (시간)
        """
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        jobs_to_remove = [
            job_id for job_id, job in self.jobs.items()
            if datetime.fromisoformat(job.get("created_at", "2000-01-01")) < cutoff_time
        ]
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
        
        if jobs_to_remove:
            logger.info(f"오래된 작업 {len(jobs_to_remove)}개 정리 완료")


# 전역 작업 큐 인스턴스
job_queue = JobQueue()

