#!/usr/bin/env python3
"""
스파이크 감지 알고리즘 성능 비교 벤치마크 스크립트
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.anomaly.spike_detector import SpikeDetector
from src.anomaly.zscore_detector import ZScoreDetector
import logging

logging.basicConfig(level=logging.WARNING)


def generate_synthetic_time_series(n=1000, spikes=5):
    """
    합성 시계열 데이터 생성 (스파이크 포함)
    
    Args:
        n: 데이터 포인트 수
        spikes: 스파이크 개수
        
    Returns:
        (values, spike_indices) 튜플
    """
    # 기본 트렌드
    trend = np.linspace(0.5, 0.6, n)
    
    # 노이즈 추가
    noise = np.random.normal(0, 0.05, n)
    
    # 주기적 패턴
    seasonal = 0.1 * np.sin(2 * np.pi * np.arange(n) / 100)
    
    values = trend + noise + seasonal
    
    # 스파이크 추가
    spike_indices = []
    for _ in range(spikes):
        idx = np.random.randint(100, n - 100)
        spike_indices.append(idx)
        values[idx] += np.random.uniform(0.3, 0.5)  # 급격한 증가
    
    # 값 범위 제한
    values = np.clip(values, 0, 1)
    
    return values.tolist(), sorted(spike_indices)


def evaluate_detection(true_spikes, detected_spikes, tolerance=5):
    """
    감지 성능 평가
    
    Args:
        true_spikes: 실제 스파이크 인덱스 리스트
        detected_spikes: 감지된 스파이크 인덱스 리스트
        tolerance: 허용 오차 (인덱스)
        
    Returns:
        (precision, recall, f1_score, false_positives) 튜플
    """
    true_set = set(true_spikes)
    detected_set = set(detected_spikes)
    
    # True Positives: 실제 스파이크 근처에서 감지된 것
    tp = 0
    for true_idx in true_set:
        for detected_idx in detected_set:
            if abs(true_idx - detected_idx) <= tolerance:
                tp += 1
                break
    
    # False Positives: 감지되었지만 실제 스파이크가 아닌 것
    fp = len(detected_set) - tp
    
    # False Negatives: 실제 스파이크인데 감지되지 않은 것
    fn = len(true_set) - tp
    
    # Precision, Recall, F1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    false_positive_rate = fp / (fp + len(true_set) - fn) if (fp + len(true_set) - fn) > 0 else 0
    
    return precision, recall, f1_score, false_positive_rate


def benchmark_algorithm(algorithm_name: str, values: list, true_spikes: list, **kwargs):
    """
    알고리즘 벤치마크 실행
    
    Args:
        algorithm_name: 알고리즘 이름
        values: 시계열 값 리스트
        true_spikes: 실제 스파이크 인덱스 리스트
        **kwargs: 알고리즘별 파라미터
        
    Returns:
        벤치마크 결과 딕셔너리
    """
    print(f"\n{'='*60}")
    print(f"벤치마크 시작: {algorithm_name}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        
        # DataFrame 생성
        df = pd.DataFrame({"value": values})
        
        # 알고리즘별 실행
        if algorithm_name == "Twitter Anomaly Detection":
            detector = SpikeDetector(threshold=kwargs.get("threshold", 2.0))
            spikes = detector.detect(df, column="value")
            detected_indices = [spike["start"] for spike in spikes]
            
        elif algorithm_name == "Percentile Method":
            # Percentile은 간단한 구현으로 대체
            threshold_value = np.percentile(values, kwargs.get("percentile", 95))
            detected_indices = [i for i, v in enumerate(values) if v >= threshold_value]
            
        elif algorithm_name == "Derivative Method":
            # Derivative는 변화율 기반
            derivatives = np.diff(values)
            threshold = kwargs.get("threshold", 0.1)
            detected_indices = [i+1 for i, d in enumerate(derivatives) if abs(d) > threshold]
            
        elif algorithm_name == "Z-score":
            detector = ZScoreDetector(threshold=kwargs.get("threshold", 2.0))
            anomalies = detector.detect(df, column="value")
            detected_indices = [anomaly["start"] for anomaly in anomalies]
            
        else:
            print(f"알 수 없는 알고리즘: {algorithm_name}")
            return None
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        # 성능 평가
        precision, recall, f1_score, fpr = evaluate_detection(true_spikes, detected_indices)
        
        result = {
            "algorithm": algorithm_name,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1_score, 2),
            "false_positive_rate": round(fpr, 2),
            "execution_time_ms": round(execution_time, 2),
            "detected_count": len(detected_indices),
            "true_count": len(true_spikes),
        }
        
        print(f"\n결과:")
        print(f"  Precision: {precision:.2f}")
        print(f"  Recall: {recall:.2f}")
        print(f"  F1-Score: {f1_score:.2f}")
        print(f"  False Positive Rate: {fpr:.2f}")
        print(f"  실행 시간: {execution_time:.2f} ms")
        print(f"  감지된 스파이크: {len(detected_indices)}개 (실제: {len(true_spikes)}개)")
        
        return result
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """메인 함수"""
    print("="*60)
    print("스파이크 감지 알고리즘 성능 비교 벤치마크")
    print("="*60)
    
    # 합성 데이터 생성
    print("\n합성 시계열 데이터 생성 중...")
    values, true_spikes = generate_synthetic_time_series(n=1000, spikes=10)
    print(f"생성 완료: {len(values)}개 데이터 포인트, {len(true_spikes)}개 스파이크")
    
    # 벤치마크할 알고리즘 목록
    algorithms = [
        ("Twitter Anomaly Detection", {}),
        ("Percentile Method", {"percentile": 95}),
        ("Derivative Method", {"threshold": 0.1}),
        ("Z-score", {"threshold": 2.0}),
    ]
    
    results = []
    for alg_name, params in algorithms:
        result = benchmark_algorithm(alg_name, values, true_spikes, **params)
        if result:
            results.append(result)
    
    # 결과 출력
    print("\n" + "="*60)
    print("최종 결과 요약")
    print("="*60)
    
    if results:
        print(f"\n{'알고리즘':<30} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'실행시간(ms)':<15}")
        print("-" * 85)
        for r in results:
            print(f"{r['algorithm']:<30} {r['precision']:<12} {r['recall']:<12} {r['f1_score']:<12} {r['execution_time_ms']:<15}")
    
    print("\n벤치마크 완료!")
    return results


if __name__ == "__main__":
    main()

