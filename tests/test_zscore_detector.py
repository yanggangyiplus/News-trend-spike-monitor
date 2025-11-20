"""
Z-score 이상치 감지기 테스트
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.anomaly.zscore_detector import ZScoreDetector


class TestZScoreDetector:
    """Z-score 감지기 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        detector = ZScoreDetector(threshold=2.0)
        assert detector.threshold == 2.0
    
    def test_detect_normal_data(self):
        """정상 데이터 테스트"""
        detector = ZScoreDetector(threshold=2.0)
        df = pd.DataFrame({
            "value": [1.0, 1.1, 1.0, 1.2, 1.1]
        })
        
        results = detector.detect(df, column="value")
        assert isinstance(results, list)
    
    def test_detect_with_anomaly(self):
        """이상치 포함 데이터 테스트"""
        detector = ZScoreDetector(threshold=2.0)
        df = pd.DataFrame({
            "value": [1.0, 1.1, 1.0, 10.0, 1.1]  # 10.0이 이상치
        })
        
        results = detector.detect(df, column="value")
        assert len(results) > 0
        assert any(r["value"] == 10.0 for r in results)
    
    def test_detect_empty_dataframe(self):
        """빈 데이터프레임 테스트"""
        detector = ZScoreDetector()
        df = pd.DataFrame({"value": []})
        
        results = detector.detect(df, column="value")
        assert len(results) == 0
    
    def test_detect_missing_column(self):
        """존재하지 않는 컬럼 테스트"""
        detector = ZScoreDetector()
        df = pd.DataFrame({"value": [1, 2, 3]})
        
        results = detector.detect(df, column="nonexistent")
        assert len(results) == 0
    
    def test_detect_with_nan(self):
        """NaN 값 포함 데이터 테스트"""
        detector = ZScoreDetector()
        df = pd.DataFrame({
            "value": [1.0, np.nan, 1.1, 1.2, np.nan]
        })
        
        results = detector.detect(df, column="value")
        assert isinstance(results, list)
    
    def test_detect_anomalies_list(self):
        """리스트 입력 테스트"""
        detector = ZScoreDetector(threshold=2.0)
        values = [1.0, 1.1, 1.0, 10.0, 1.1]
        
        indices = detector.detect_anomalies(values, return_indices=True)
        assert isinstance(indices, list)
        assert len(indices) > 0

