#!/usr/bin/env python3
"""
감정 분석 모델 Latency 벤치마크 스크립트
"""

import sys
import time
import statistics
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.nlp.sentiment_analyzer import SentimentAnalyzer
import logging

logging.basicConfig(level=logging.WARNING)  # 로그 레벨 낮춤


def generate_test_texts(n=100):
    """테스트용 텍스트 생성"""
    positive_samples = [
        "이것은 매우 긍정적인 뉴스입니다. 좋은 소식이네요.",
        "회사가 큰 성과를 거두었습니다. 축하합니다.",
        "새로운 기술이 개발되어 기대가 큽니다.",
    ]
    
    negative_samples = [
        "이것은 부정적인 뉴스입니다. 걱정이 됩니다.",
        "문제가 발생했습니다. 해결이 필요합니다.",
        "어려운 상황이 계속되고 있습니다.",
    ]
    
    neutral_samples = [
        "이것은 중립적인 뉴스입니다. 정보를 전달합니다.",
        "일반적인 뉴스 내용입니다.",
        "상황을 알려드립니다.",
    ]
    
    # 샘플을 반복하여 n개 생성
    all_samples = (positive_samples + negative_samples + neutral_samples) * (n // 9 + 1)
    return all_samples[:n]


def benchmark_model(model_name: str, test_texts: list, warmup_rounds: int = 5):
    """
    모델 벤치마크 실행
    
    Args:
        model_name: 모델 이름
        test_texts: 테스트 텍스트 리스트
        warmup_rounds: 워밍업 라운드 수
        
    Returns:
        벤치마크 결과 딕셔너리
    """
    print(f"\n{'='*60}")
    print(f"벤치마크 시작: {model_name}")
    print(f"{'='*60}")
    
    try:
        # 모델 초기화
        print("모델 초기화 중...")
        analyzer = SentimentAnalyzer(model_name=model_name, device="cpu")
        
        # 워밍업
        print(f"워밍업 중 ({warmup_rounds}회)...")
        warmup_texts = test_texts[:warmup_rounds]
        for text in warmup_texts:
            try:
                analyzer.analyze(text)
            except:
                pass
        
        # 실제 벤치마크
        print(f"벤치마크 실행 중 ({len(test_texts)}개 샘플)...")
        latencies = []
        
        for i, text in enumerate(test_texts):
            start = time.time()
            try:
                result = analyzer.analyze(text)
                latency_ms = (time.time() - start) * 1000
                latencies.append(latency_ms)
            except Exception as e:
                print(f"  샘플 {i+1} 처리 실패: {e}")
                continue
            
            if (i + 1) % 20 == 0:
                print(f"  진행: {i+1}/{len(test_texts)}")
        
        if not latencies:
            return None
        
        # 통계 계산
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        min_latency = min(latencies)
        max_latency = max(latencies)
        std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        result = {
            "model_name": model_name,
            "samples": len(latencies),
            "avg_latency_ms": round(avg_latency, 2),
            "median_latency_ms": round(median_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "min_latency_ms": round(min_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "std_latency_ms": round(std_latency, 2),
        }
        
        print(f"\n결과:")
        print(f"  평균 Latency: {avg_latency:.2f} ms")
        print(f"  중앙값 Latency: {median_latency:.2f} ms")
        print(f"  P95 Latency: {p95_latency:.2f} ms")
        print(f"  최소/최대: {min_latency:.2f} / {max_latency:.2f} ms")
        
        return result
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """메인 함수"""
    print("="*60)
    print("감정 분석 모델 Latency 벤치마크")
    print("="*60)
    
    # 테스트 텍스트 생성
    test_texts = generate_test_texts(n=50)  # 빠른 테스트를 위해 50개로 제한
    
    # 벤치마크할 모델 목록
    models = [
        "beomi/KcELECTRA-base",
        # 다른 모델들은 시간이 오래 걸릴 수 있으므로 선택적으로 실행
        # "bert-base-multilingual-cased",
        # "distilbert-base-multilingual-cased",
    ]
    
    results = []
    for model_name in models:
        result = benchmark_model(model_name, test_texts)
        if result:
            results.append(result)
    
    # 결과 출력
    print("\n" + "="*60)
    print("최종 결과 요약")
    print("="*60)
    
    if results:
        print(f"\n{'모델':<40} {'평균(ms)':<12} {'P95(ms)':<12} {'샘플 수':<10}")
        print("-" * 80)
        for r in results:
            print(f"{r['model_name']:<40} {r['avg_latency_ms']:<12} {r['p95_latency_ms']:<12} {r['samples']:<10}")
    
    print("\n벤치마크 완료!")
    return results


if __name__ == "__main__":
    main()

