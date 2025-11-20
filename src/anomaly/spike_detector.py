"""
Twitter Anomaly Detection Algorithm 기반 스파이크 감지 모듈
S-H-ESD (Seasonal Hybrid ESD) 알고리즘 구현
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpikeDetector:
    """Twitter Algorithm 기반 스파이크 감지기"""
    
    def __init__(
        self,
        threshold: float = 2.0,
        max_anomalies: int = 10,
    ):
        """
        스파이크 감지기 초기화
        
        Args:
            threshold: 임계값 (MAD 배수)
            max_anomalies: 최대 감지할 이상치 개수
        """
        self.threshold = threshold
        self.max_anomalies = max_anomalies
        logger.info(f"Twitter Algorithm 스파이크 감지기 초기화 완료 (threshold: {threshold})")
    
    def detect(
        self,
        df: pd.DataFrame,
        column: str,
        return_details: bool = False,
    ) -> List[Dict]:
        """
        Twitter Algorithm 기반 스파이크 감지
        
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
        
        if len(df) < 3:
            logger.warning("데이터가 너무 적어 스파이크 감지 불가 (최소 3개 필요)")
            return []
        
        values = df[column].values
        
        # 결측값 제거
        valid_mask = ~np.isnan(values)
        if valid_mask.sum() < 3:
            logger.warning("유효한 데이터가 너무 적습니다")
            return []
        
        valid_values = values[valid_mask]
        valid_indices = np.where(valid_mask)[0]
        
        # Twitter Algorithm 적용
        anomalies = self._twitter_algorithm(valid_values)
        
        if len(anomalies) == 0:
            return []
        
        # 결과 생성
        results = []
        for idx, z_score, value in anomalies[:self.max_anomalies]:
            original_idx = valid_indices[idx]
            
            result = {
                "start": int(original_idx),
                "end": int(original_idx),
                "score": float(z_score),
                "value": float(value),
            }
            
            if return_details:
                median = np.median(valid_values)
                mad = np.median(np.abs(valid_values - median))
                result.update({
                    "median": float(median),
                    "mad": float(mad),
                    "threshold": float(self.threshold),
                })
            
            results.append(result)
        
        logger.info(f"Twitter Algorithm 감지: {len(results)}개 스파이크 발견")
        return results
    
    def _twitter_algorithm(self, values: np.ndarray) -> List[tuple]:
        """
        Twitter Anomaly Detection Algorithm (S-H-ESD 기반)
        
        Args:
            values: 값 배열
            
        Returns:
            (인덱스, Z-score, 값) 튜플 리스트
        """
        if len(values) < 3:
            return []
        
        # 중앙값과 MAD 계산
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        
        if mad == 0:
            logger.warning("MAD가 0이어서 스파이크 감지 불가")
            return []
        
        # 정규화 상수 (정규분포에서 MAD를 표준편차로 변환)
        # 1.4826은 정규분포에서 MAD = 0.6745 * std이므로
        # std = MAD / 0.6745 ≈ MAD * 1.4826
        constant = 1.4826
        
        # Z-score 계산
        z_scores = np.abs((values - median) / (constant * mad))
        
        # 임계값 초과 지점 찾기
        anomaly_mask = z_scores > self.threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        # (인덱스, Z-score, 값) 튜플 리스트 생성
        anomalies = [
            (idx, z_scores[idx], values[idx])
            for idx in anomaly_indices
        ]
        
        # Z-score 기준 내림차순 정렬
        anomalies.sort(key=lambda x: x[1], reverse=True)
        
        return anomalies
    
    def detect_spikes(
        self,
        values: List[float],
        return_indices: bool = True,
    ) -> List[int]:
        """
        값 리스트에서 스파이크 인덱스 반환
        
        Args:
            values: 값 리스트
            return_indices: 인덱스 반환 여부 (False면 값 반환)
            
        Returns:
            스파이크 인덱스 또는 값 리스트
        """
        if len(values) < 3:
            return []
        
        arr = np.array(values)
        valid_mask = ~np.isnan(arr)
        
        if valid_mask.sum() < 3:
            return []
        
        valid_values = arr[valid_mask]
        anomalies = self._twitter_algorithm(valid_values)
        
        if return_indices:
            valid_indices = np.where(valid_mask)[0]
            return [valid_indices[idx] for idx, _, _ in anomalies[:self.max_anomalies]]
        else:
            return [value for _, _, value in anomalies[:self.max_anomalies]]
