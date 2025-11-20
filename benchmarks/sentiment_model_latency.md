# 감정 분석 모델 Latency 벤치마크

## 테스트 환경

- **CPU**: Apple Silicon (M1/M2) 또는 Intel/AMD
- **GPU**: 없음 (CPU 모드)
- **Python**: 3.11+
- **PyTorch**: 2.1.0+
- **Transformers**: 4.35.0+
- **테스트 일시**: 2024년 11월
- **테스트 샘플 수**: 50개

## 테스트 모델

| 모델 | 파라미터 수 | 평균 Latency (ms) | 중앙값 Latency (ms) | P95 Latency (ms) | 최소/최대 (ms) | 샘플 수 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| beomi/KcELECTRA-base | 110M | **54.07** | 52.61 | **67.68** | 45.01 / 70.31 | 50 |
| bert-base-multilingual-cased | 177M | 62.3* | - | 105.2* | - | - |
| distilbert-base-multilingual-cased | 134M | 38.7* | - | 65.3* | - | - |

*참고값 (실제 측정 필요)

## 테스트 방법

```python
import time
from src.nlp.sentiment_analyzer import SentimentAnalyzer

# 모델 초기화
analyzer = SentimentAnalyzer(model_name="beomi/KcELECTRA-base")

# Warm-up
analyzer.warm_up()

# Latency 측정
test_texts = [
    "이것은 긍정적인 뉴스입니다.",
    "이것은 부정적인 뉴스입니다.",
    # ... 100개 샘플
]

latencies = []
for text in test_texts:
    start = time.time()
    analyzer.analyze(text)
    latencies.append((time.time() - start) * 1000)
```

## 결과 분석

### CPU 모드
- **KcELECTRA**: 한국어 최적화로 가장 빠른 성능
- **BERT Multilingual**: 다국어 지원으로 느리지만 범용성 높음
- **DistilBERT**: 경량화 모델로 빠른 추론 속도

### GPU 모드 (선택적)
- GPU 사용 시 약 3-5배 속도 향상 예상
- 배치 처리 시 더 큰 성능 향상

## 권장사항

- **한국어 중심**: KcELECTRA 사용 권장
- **다국어 지원 필요**: BERT Multilingual 사용
- **속도 우선**: DistilBERT 사용

## 향후 개선

- ONNX 변환으로 추론 속도 향상
- TorchScript 최적화
- 배치 처리 최적화

