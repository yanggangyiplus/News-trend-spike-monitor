"""
공통 예외 클래스 정의
"""


class NewsTrendMonitorError(Exception):
    """기본 예외 클래스"""
    
    def __init__(self, message: str, error_code: str = None):
        """
        예외 초기화
        
        Args:
            message: 에러 메시지
            error_code: 에러 코드 (선택사항)
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DataCollectionError(NewsTrendMonitorError):
    """데이터 수집 관련 예외"""
    pass


class RSSCollectionError(DataCollectionError):
    """RSS 수집 오류"""
    pass


class GoogleNewsAPIError(DataCollectionError):
    """Google News API 오류"""
    pass


class PreprocessingError(NewsTrendMonitorError):
    """전처리 관련 예외"""
    pass


class SentimentAnalysisError(NewsTrendMonitorError):
    """감정 분석 관련 예외"""
    pass


class AnomalyDetectionError(NewsTrendMonitorError):
    """이상치 감지 관련 예외"""
    pass


class SpikeDetectionError(NewsTrendMonitorError):
    """스파이크 감지 관련 예외"""
    pass


class ConfigurationError(NewsTrendMonitorError):
    """설정 관련 예외"""
    pass

