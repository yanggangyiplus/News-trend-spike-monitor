"""
스파이크 감지기 테스트
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.anomaly.spike_detector import SpikeDetector


class TestSpikeDetector:
    """스파이크 감지기 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        detector = SpikeDetector(threshold=2.0)
        assert detector.threshold == 2.0
        assert detector.max_anomalies == 10
    
    def test_detect_normal_data(self):
        """정상 데이터 테스트"""
        detector = SpikeDetector(threshold=2.0)
        df = pd.DataFrame({
            "value": [1.0, 1.1, 1.0, 1.2, 1.1]
        })
        
        results = detector.detect(df, column="value")
        assert isinstance(results, list)
    
    def test_detect_with_spike(self):
        """스파이크 포함 데이터 테스트"""
        detector = SpikeDetector(threshold=2.0)
        df = pd.DataFrame({
            "value": [1.0, 1.1, 1.0, 5.0, 1.1]  # 5.0이 스파이크
        })
        
        results = detector.detect(df, column="value")
        assert isinstance(results, list)
    
    def test_detect_insufficient_data(self):
        """데이터 부족 테스트"""
        detector = SpikeDetector()
        df = pd.DataFrame({
            "value": [1.0, 1.1]  # 최소 3개 필요
        })
        
        results = detector.detect(df, column="value")
        assert len(results) == 0
    
    def test_detect_missing_column(self):
        """존재하지 않는 컬럼 테스트"""
        detector = SpikeDetector()
        df = pd.DataFrame({"value": [1, 2, 3]})
        
        results = detector.detect(df, column="nonexistent")
        assert len(results) == 0
    
    def test_detect_spikes_list(self):
        """리스트 입력 테스트"""
        detector = SpikeDetector(threshold=2.0)
        values = [1.0, 1.1, 1.0, 5.0, 1.1]
        
        indices = detector.detect_spikes(values, return_indices=True)
        assert isinstance(indices, list)

