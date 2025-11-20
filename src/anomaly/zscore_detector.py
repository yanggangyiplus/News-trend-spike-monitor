"""
Z-score 기반 이상치 감지 모듈
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ZScoreDetector:
    """Z-score 기반 이상치 감지기"""
    
    def __init__(self, threshold: float = 2.0):
        """
        Z-score 감지기 초기화
        
        Args:
            threshold: Z-score 임계값 (기본값: 2.0 = 2 표준편차)
        """
        self.threshold = threshold
        logger.info(f"Z-score 감지기 초기화 완료 (threshold: {threshold})")
    
    def detect(
        self,
        df: pd.DataFrame,
        column: str,
        return_details: bool = False,
    ) -> List[Dict]:
        """
        Z-score 기반 이상치 감지
        
        Args:
            df: 시계열 데이터프레임
            column: 분석할 컬럼명
            return_details: 상세 정보 반환 여부
            
        Returns:
            스파이크 구간 리스트
            [{'start': idx, 'end': idx, 'score': z_score, 'value': value}, ...]
        """
        if column not in df.columns:
            logger.error(f"컬럼 '{column}'이 데이터프레임에 없습니다")
            return []
        
        if len(df) < 2:
            logger.warning("데이터가 너무 적어 이상치 감지 불가")
            return []
        
        values = df[column].values
        
        # 결측값 제거
        valid_mask = ~np.isnan(values)
        if valid_mask.sum() < 2:
            logger.warning("유효한 데이터가 너무 적습니다")
            return []
        
        valid_values = values[valid_mask]
        valid_indices = np.where(valid_mask)[0]
        
        # 평균과 표준편차 계산
        mean = np.mean(valid_values)
        std = np.std(valid_values)
        
        if std == 0:
            logger.warning("표준편차가 0이어서 이상치 감지 불가")
            return []
        
        # Z-score 계산
        z_scores = np.abs((valid_values - mean) / std)
        
        # 이상치 인덱스 찾기
        anomaly_mask = z_scores > self.threshold
        anomaly_indices = valid_indices[anomaly_mask]
        anomaly_z_scores = z_scores[anomaly_mask]
        anomaly_values = valid_values[anomaly_mask]
        
        # 결과 생성
        results = []
        for idx, z_score, value in zip(anomaly_indices, anomaly_z_scores, anomaly_values):
            result = {
                "start": int(idx),
                "end": int(idx),
                "score": float(z_score),
                "value": float(value),
            }
            
            if return_details:
                result.update({
                    "mean": float(mean),
                    "std": float(std),
                    "threshold": float(self.threshold),
                })
            
            results.append(result)
        
        logger.info(f"Z-score 감지: {len(results)}개 이상치 발견")
        return results
    
    def detect_anomalies(
        self,
        values: List[float],
        return_indices: bool = True,
    ) -> List[int]:
        """
        값 리스트에서 이상치 인덱스 반환
        
        Args:
            values: 값 리스트
            return_indices: 인덱스 반환 여부 (False면 값 반환)
            
        Returns:
            이상치 인덱스 또는 값 리스트
        """
        if len(values) < 2:
            return []
        
        arr = np.array(values)
        valid_mask = ~np.isnan(arr)
        
        if valid_mask.sum() < 2:
            return []
        
        valid_values = arr[valid_mask]
        mean = np.mean(valid_values)
        std = np.std(valid_values)
        
        if std == 0:
            return []
        
        z_scores = np.abs((valid_values - mean) / std)
        anomaly_mask = z_scores > self.threshold
        
        if return_indices:
            return np.where(valid_mask)[0][anomaly_mask].tolist()
        else:
            return valid_values[anomaly_mask].tolist()

