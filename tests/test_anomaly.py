"""
이상치 감지 모듈 테스트
"""

import pytest
from src.anomaly.detector import AnomalyDetector


def test_zscore_detection():
    """Z-score 기반 이상치 감지 테스트"""
    detector = AnomalyDetector(method="zscore")
    
    # 정상 데이터
    values = [1.0, 1.1, 1.0, 1.2, 1.1]
    anomalies = detector.detect(values, threshold=2.0)
    assert sum(anomalies) == 0
    
    # 이상치 포함 데이터
    values = [1.0, 1.1, 1.0, 10.0, 1.1]  # 10.0이 이상치
    anomalies = detector.detect(values, threshold=2.0)
    assert sum(anomalies) > 0


def test_esd_detection():
    """ESD 기반 이상치 감지 테스트"""
    detector = AnomalyDetector(method="esd")
    
    values = [1.0, 1.1, 1.0, 10.0, 1.1]
    anomalies = detector.detect(values, threshold=2.0)
    assert isinstance(anomalies, list)
    assert len(anomalies) == len(values)


def test_moving_avg_detection():
    """Moving Average 기반 이상치 감지 테스트"""
    detector = AnomalyDetector(method="moving_avg")
    
    values = [1.0, 1.1, 1.0, 1.2, 1.1, 10.0]
    anomalies = detector.detect(values, threshold=2.0)
    assert isinstance(anomalies, list)
    assert len(anomalies) == len(values)

