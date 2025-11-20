"""
이상치 감지 모듈
Z-score, ESD test, Moving Average Deviation 등 다양한 방법 구현
"""

import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """이상치 감지기 클래스"""
    
    def __init__(self, method: str = "zscore"):
        """
        이상치 감지기 초기화
        
        Args:
            method: 감지 방법 ('zscore', 'esd', 'moving_avg')
        """
        self.method = method
        logger.info(f"이상치 감지기 초기화 완료: {method}")
    
    def detect(self, values: List[float], threshold: float = 2.0) -> List[bool]:
        """
        이상치 감지
        
        Args:
            values: 시계열 값 리스트
            threshold: 임계값
            
        Returns:
            이상치 여부 리스트 (True=이상치)
        """
        if self.method == "zscore":
            return self._detect_zscore(values, threshold)
        elif self.method == "esd":
            return self._detect_esd(values, threshold)
        elif self.method == "moving_avg":
            return self._detect_moving_avg(values, threshold)
        else:
            logger.warning(f"알 수 없는 방법: {self.method}, zscore 사용")
            return self._detect_zscore(values, threshold)
    
    def _detect_zscore(self, values: List[float], threshold: float) -> List[bool]:
        """
        Z-score 기반 이상치 감지
        
        Args:
            values: 시계열 값 리스트
            threshold: Z-score 임계값
            
        Returns:
            이상치 여부 리스트
        """
        if len(values) < 2:
            return [False] * len(values)
        
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std == 0:
            return [False] * len(values)
        
        z_scores = np.abs((arr - mean) / std)
        anomalies = z_scores > threshold
        
        logger.debug(f"Z-score 감지: {np.sum(anomalies)}개 이상치 발견")
        return anomalies.tolist()
    
    def _detect_esd(self, values: List[float], threshold: float) -> List[bool]:
        """
        ESD (Extreme Studentized Deviate) 테스트 기반 이상치 감지
        
        Args:
            values: 시계열 값 리스트
            threshold: 임계값
            
        Returns:
            이상치 여부 리스트
        """
        if len(values) < 3:
            return [False] * len(values)
        
        arr = np.array(values)
        anomalies = [False] * len(values)
        
        # 간단한 ESD 구현
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std == 0:
            return anomalies
        
        for i, val in enumerate(arr):
            z_score = abs((val - mean) / std)
            if z_score > threshold:
                anomalies[i] = True
        
        logger.debug(f"ESD 감지: {np.sum(anomalies)}개 이상치 발견")
        return anomalies
    
    def _detect_moving_avg(self, values: List[float], threshold: float, window: int = 5) -> List[bool]:
        """
        Moving Average Deviation 기반 이상치 감지
        
        Args:
            values: 시계열 값 리스트
            threshold: 임계값
            window: 이동 평균 윈도우 크기
            
        Returns:
            이상치 여부 리스트
        """
        if len(values) < window + 1:
            return [False] * len(values)
        
        arr = np.array(values)
        anomalies = [False] * len(values)
        
        # 이동 평균 계산
        moving_avg = np.convolve(arr, np.ones(window) / window, mode="valid")
        
        # 표준 편차 계산
        std = np.std(arr)
        
        if std == 0:
            return anomalies
        
        # 이동 평균과의 편차 확인
        for i in range(window - 1, len(arr)):
            ma_value = moving_avg[i - window + 1]
            deviation = abs(arr[i] - ma_value) / std
            
            if deviation > threshold:
                anomalies[i] = True
        
        logger.debug(f"Moving Average 감지: {np.sum(anomalies)}개 이상치 발견")
        return anomalies
    
    def get_anomaly_indices(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """
        이상치 인덱스 반환
        
        Args:
            values: 시계열 값 리스트
            threshold: 임계값
            
        Returns:
            이상치 인덱스 리스트
        """
        anomalies = self.detect(values, threshold)
        return [i for i, is_anomaly in enumerate(anomalies) if is_anomaly]

