"""
서비스 모니터링 모듈
API 응답 시간, 모델 추론 latency, 스파이크 탐지 시간 측정
"""

import time
from typing import Dict, Optional
from datetime import datetime
from collections import defaultdict
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class MetricsCollector:
    """메트릭 수집기 클래스"""
    
    def __init__(self):
        """메트릭 수집기 초기화"""
        self.api_response_times: list = []
        self.nlp_latencies: list = []
        self.spike_detection_times: list = []
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.service_start_time = datetime.now()
        
        logger.info("메트릭 수집기 초기화 완료")
    
    def record_api_response_time(self, endpoint: str, duration: float):
        """
        API 응답 시간 기록
        
        Args:
            endpoint: 엔드포인트 이름
            duration: 응답 시간 (초)
        """
        self.api_response_times.append({
            "endpoint": endpoint,
            "duration": duration,
            "timestamp": datetime.now(),
        })
        
        # 최근 1000개만 유지
        if len(self.api_response_times) > 1000:
            self.api_response_times = self.api_response_times[-1000:]
    
    def record_nlp_latency(self, model_name: str, duration: float):
        """
        NLP 모델 추론 latency 기록
        
        Args:
            model_name: 모델 이름
            duration: 추론 시간 (초)
        """
        self.nlp_latencies.append({
            "model": model_name,
            "duration": duration,
            "timestamp": datetime.now(),
        })
        
        # 최근 1000개만 유지
        if len(self.nlp_latencies) > 1000:
            self.nlp_latencies = self.nlp_latencies[-1000:]
    
    def record_spike_detection_time(self, method: str, duration: float):
        """
        스파이크 탐지 시간 기록
        
        Args:
            method: 탐지 방법
            duration: 탐지 시간 (초)
        """
        self.spike_detection_times.append({
            "method": method,
            "duration": duration,
            "timestamp": datetime.now(),
        })
        
        # 최근 1000개만 유지
        if len(self.spike_detection_times) > 1000:
            self.spike_detection_times = self.spike_detection_times[-1000:]
    
    def increment_request_count(self, endpoint: str):
        """요청 카운트 증가"""
        self.request_counts[endpoint] += 1
    
    def increment_error_count(self, endpoint: str, error_type: str = "unknown"):
        """에러 카운트 증가"""
        key = f"{endpoint}:{error_type}"
        self.error_counts[key] += 1
    
    def get_metrics_summary(self) -> Dict:
        """
        메트릭 요약 정보 반환
        
        Returns:
            메트릭 요약 딕셔너리
        """
        # API 응답 시간 통계
        api_durations = [m["duration"] for m in self.api_response_times[-100:]]
        api_avg = sum(api_durations) / len(api_durations) if api_durations else 0.0
        api_max = max(api_durations) if api_durations else 0.0
        
        # NLP latency 통계
        nlp_durations = [m["duration"] for m in self.nlp_latencies[-100:]]
        nlp_avg = sum(nlp_durations) / len(nlp_durations) if nlp_durations else 0.0
        nlp_max = max(nlp_durations) if nlp_durations else 0.0
        
        # 스파이크 탐지 시간 통계
        spike_durations = [m["duration"] for m in self.spike_detection_times[-100:]]
        spike_avg = sum(spike_durations) / len(spike_durations) if spike_durations else 0.0
        spike_max = max(spike_durations) if spike_durations else 0.0
        
        # 서비스 가동 시간
        uptime = (datetime.now() - self.service_start_time).total_seconds()
        
        return {
            "api_response_time": {
                "avg": api_avg,
                "max": api_max,
                "count": len(api_durations),
            },
            "nlp_latency": {
                "avg": nlp_avg,
                "max": nlp_max,
                "count": len(nlp_durations),
            },
            "spike_detection_time": {
                "avg": spike_avg,
                "max": spike_max,
                "count": len(spike_durations),
            },
            "request_counts": dict(self.request_counts),
            "error_counts": dict(self.error_counts),
            "uptime_seconds": uptime,
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_prometheus_metrics(self) -> str:
        """
        Prometheus 포맷 메트릭 반환
        
        Returns:
            Prometheus 포맷 문자열
        """
        summary = self.get_metrics_summary()
        
        metrics = []
        
        # API 응답 시간
        metrics.append(f"# HELP api_response_time_seconds API 응답 시간")
        metrics.append(f"# TYPE api_response_time_seconds summary")
        metrics.append(f'api_response_time_seconds{{quantile="0.5"}} {summary["api_response_time"]["avg"]}')
        metrics.append(f'api_response_time_seconds{{quantile="0.95"}} {summary["api_response_time"]["max"]}')
        metrics.append(f'api_response_time_seconds_count {summary["api_response_time"]["count"]}')
        
        # NLP latency
        metrics.append(f"# HELP nlp_latency_seconds NLP 모델 추론 시간")
        metrics.append(f"# TYPE nlp_latency_seconds summary")
        metrics.append(f'nlp_latency_seconds{{quantile="0.5"}} {summary["nlp_latency"]["avg"]}')
        metrics.append(f'nlp_latency_seconds{{quantile="0.95"}} {summary["nlp_latency"]["max"]}')
        metrics.append(f'nlp_latency_seconds_count {summary["nlp_latency"]["count"]}')
        
        # 스파이크 탐지 시간
        metrics.append(f"# HELP spike_detection_time_seconds 스파이크 탐지 시간")
        metrics.append(f"# TYPE spike_detection_time_seconds summary")
        metrics.append(f'spike_detection_time_seconds{{quantile="0.5"}} {summary["spike_detection_time"]["avg"]}')
        metrics.append(f'spike_detection_time_seconds{{quantile="0.95"}} {summary["spike_detection_time"]["max"]}')
        metrics.append(f'spike_detection_time_seconds_count {summary["spike_detection_time"]["count"]}')
        
        # 요청 카운트
        metrics.append(f"# HELP request_count_total 총 요청 수")
        metrics.append(f"# TYPE request_count_total counter")
        for endpoint, count in summary["request_counts"].items():
            metrics.append(f'request_count_total{{endpoint="{endpoint}"}} {count}')
        
        # 에러 카운트
        metrics.append(f"# HELP error_count_total 총 에러 수")
        metrics.append(f"# TYPE error_count_total counter")
        for error_key, count in summary["error_counts"].items():
            endpoint, error_type = error_key.split(":", 1)
            metrics.append(f'error_count_total{{endpoint="{endpoint}",error_type="{error_type}"}} {count}')
        
        # 서비스 가동 시간
        metrics.append(f"# HELP service_uptime_seconds 서비스 가동 시간")
        metrics.append(f"# TYPE service_uptime_seconds gauge")
        metrics.append(f'service_uptime_seconds {summary["uptime_seconds"]}')
        
        return "\n".join(metrics)


# 전역 메트릭 수집기 인스턴스
metrics_collector = MetricsCollector()


def monitor_api_response(endpoint: str):
    """
    API 응답 시간 모니터링 데코레이터
    
    Args:
        endpoint: 엔드포인트 이름
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics_collector.increment_request_count(endpoint)
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_api_response_time(endpoint, duration)
                return result
            except Exception as e:
                metrics_collector.increment_error_count(endpoint, type(e).__name__)
                raise
        
        return wrapper
    return decorator


def monitor_nlp_latency(model_name: str):
    """
    NLP 모델 latency 모니터링 데코레이터
    
    Args:
        model_name: 모델 이름
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metrics_collector.record_nlp_latency(model_name, duration)
            return result
        
        return wrapper
    return decorator


def monitor_spike_detection(method: str):
    """
    스파이크 탐지 시간 모니터링 데코레이터
    
    Args:
        method: 탐지 방법
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metrics_collector.record_spike_detection_time(method, duration)
            return result
        
        return wrapper
    return decorator

