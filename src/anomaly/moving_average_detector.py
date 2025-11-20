"""
Moving Average 기반 이상치 감지 모듈
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MovingAverageDetector:
    """Moving Average 기반 이상치 감지기"""
    
    def __init__(
        self,
        window_size: int = 5,
        threshold: float = 2.0,
    ):
        """
        Moving Average 감지기 초기화
        
        Args:
            window_size: 이동 평균 윈도우 크기
            threshold: 표준편차 배수 임계값
        """
        self.window_size = window_size
        self.threshold = threshold
        logger.info(f"Moving Average 감지기 초기화 완료 (window: {window_size}, threshold: {threshold})")
    
    def detect(
        self,
        df: pd.DataFrame,
        column: str,
        return_details: bool = False,
    ) -> List[Dict]:
        """
        Moving Average 기반 이상치 감지
        
        Args:
            df: 시계열 데이터프레임
            column: 분석할 컬럼명
            return_details: 상세 정보 반환 여부
            
        Returns:
            스파이크 구간 리스트
            [{'start': idx, 'end': idx, 'score': deviation, 'value': value}, ...]
        """
        if column not in df.columns:
            logger.error(f"컬럼 '{column}'이 데이터프레임에 없습니다")
            return []
        
        if len(df) < self.window_size + 1:
            logger.warning(f"데이터가 너무 적어 이상치 감지 불가 (최소 {self.window_size + 1}개 필요)")
            return []
        
        values = df[column].values
        
        # 결측값 처리
        valid_mask = ~np.isnan(values)
        if valid_mask.sum() < self.window_size + 1:
            logger.warning("유효한 데이터가 너무 적습니다")
            return []
        
        # 이동 평균 계산
        moving_avg = self._calculate_moving_average(values, valid_mask)
        
        if moving_avg is None:
            return []
        
        # 편차 계산
        deviations = np.abs(values - moving_avg)
        
        # 표준편차 계산
        std = np.std(values[valid_mask])
        
        if std == 0:
            logger.warning("표준편차가 0이어서 이상치 감지 불가")
            return []
        
        # 정규화된 편차 (Z-score)
        normalized_deviations = deviations / std
        
        # 이상치 인덱스 찾기
        anomaly_mask = (normalized_deviations > self.threshold) & valid_mask
        anomaly_indices = np.where(anomaly_mask)[0]
        
        # 결과 생성
        results = []
        for idx in anomaly_indices:
            result = {
                "start": int(idx),
                "end": int(idx),
                "score": float(normalized_deviations[idx]),
                "value": float(values[idx]),
            }
            
            if return_details:
                result.update({
                    "moving_avg": float(moving_avg[idx]),
                    "deviation": float(deviations[idx]),
                    "threshold": float(self.threshold),
                    "window_size": int(self.window_size),
                })
            
            results.append(result)
        
        logger.info(f"Moving Average 감지: {len(results)}개 이상치 발견")
        return results
    
    def _calculate_moving_average(
        self,
        values: np.ndarray,
        valid_mask: np.ndarray,
    ) -> Optional[np.ndarray]:
        """
        이동 평균 계산
        
        Args:
            values: 값 배열
            valid_mask: 유효한 값 마스크
            
        Returns:
            이동 평균 배열
        """
        try:
            moving_avg = np.full_like(values, np.nan, dtype=float)
            
            # 유효한 값들에 대해서만 이동 평균 계산
            valid_indices = np.where(valid_mask)[0]
            
            for i in range(self.window_size, len(valid_indices)):
                window_start = valid_indices[i - self.window_size]
                window_end = valid_indices[i]
                
                # 윈도우 내 유효한 값들만 사용
                window_values = values[window_start:window_end + 1]
                window_valid = valid_mask[window_start:window_end + 1]
                
                if window_valid.sum() > 0:
                    moving_avg[valid_indices[i]] = np.mean(window_values[window_valid])
            
            return moving_avg
        
        except Exception as e:
            logger.error(f"이동 평균 계산 오류: {e}")
            return None
    
    def detect_anomalies(
        self,
        values: List[float],
        return_indices: bool = True,
    ) -> List[int]:
        """
        값 리스트에서 이상치 인덱스 반환
        
        Args:
            values: 값 리스트
            return_indices: 인덱스 반환 여부
            
        Returns:
            이상치 인덱스 리스트
        """
        if len(values) < self.window_size + 1:
            return []
        
        arr = np.array(values)
        valid_mask = ~np.isnan(arr)
        
        if valid_mask.sum() < self.window_size + 1:
            return []
        
        moving_avg = self._calculate_moving_average(arr, valid_mask)
        
        if moving_avg is None:
            return []
        
        deviations = np.abs(arr - moving_avg)
        std = np.std(arr[valid_mask])
        
        if std == 0:
            return []
        
        normalized_deviations = deviations / std
        anomaly_mask = (normalized_deviations > self.threshold) & valid_mask
        
        if return_indices:
            return np.where(anomaly_mask)[0].tolist()
        else:
            return arr[anomaly_mask].tolist()

