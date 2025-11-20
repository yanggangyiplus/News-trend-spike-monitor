"""
FastAPI 응답 캐싱 모듈
"""

from typing import Optional, Any
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """인메모리 캐시 클래스"""
    
    def __init__(self, default_ttl: int = 600):
        """
        캐시 초기화
        
        Args:
            default_ttl: 기본 TTL (초)
        """
        self.cache: dict = {}
        self.default_ttl = default_ttl
        logger.info(f"인메모리 캐시 초기화 완료 (TTL: {default_ttl}초)")
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        캐시 키 생성
        
        Args:
            prefix: 키 접두사
            **kwargs: 키워드 인자
            
        Returns:
            캐시 키 문자열
        """
        key_str = f"{prefix}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """
        캐시에서 값 가져오기
        
        Args:
            prefix: 키 접두사
            **kwargs: 키워드 인자
            
        Returns:
            캐시된 값 또는 None
        """
        key = self._generate_key(prefix, **kwargs)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # TTL 확인
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            logger.debug(f"캐시 만료: {key}")
            return None
        
        logger.debug(f"캐시 히트: {key}")
        return entry["value"]
    
    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, **kwargs):
        """
        캐시에 값 저장
        
        Args:
            prefix: 키 접두사
            value: 저장할 값
            ttl: TTL (초), None이면 기본값 사용
            **kwargs: 키워드 인자
        """
        key = self._generate_key(prefix, **kwargs)
        ttl = ttl or self.default_ttl
        
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "created_at": datetime.now(),
        }
        
        logger.debug(f"캐시 저장: {key} (TTL: {ttl}초)")
    
    def delete(self, prefix: str, **kwargs):
        """
        캐시에서 값 삭제
        
        Args:
            prefix: 키 접두사
            **kwargs: 키워드 인자
        """
        key = self._generate_key(prefix, **kwargs)
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"캐시 삭제: {key}")
    
    def clear(self):
        """캐시 전체 삭제"""
        self.cache.clear()
        logger.info("캐시 전체 삭제 완료")
    
    def cleanup_expired(self):
        """만료된 항목 정리"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"만료된 캐시 항목 {len(expired_keys)}개 정리 완료")


# 전역 캐시 인스턴스
cache = InMemoryCache(default_ttl=600)


def cache_response(ttl: int = 600):
    """
    응답 캐싱 데코레이터
    
    Args:
        ttl: TTL (초)
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}"
            cached_value = cache.get(cache_key, **kwargs)
            
            if cached_value is not None:
                return cached_value
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐싱
            cache.set(cache_key, result, ttl=ttl, **kwargs)
            
            return result
        
        return wrapper
    return decorator

