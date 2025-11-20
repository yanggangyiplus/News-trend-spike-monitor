# 벤치마크 실행 가이드

이 디렉토리에는 프로젝트의 성능 벤치마크 스크립트와 결과 문서가 포함되어 있습니다.

## 벤치마크 스크립트

### 1. 감정 분석 모델 Latency 벤치마크

```bash
python3 benchmarks/run_sentiment_benchmark.py
```

**기능**:
- 다양한 NLP 모델의 추론 속도 측정
- 평균, 중앙값, P95 Latency 계산
- 메모리 사용량 측정

**결과**: `sentiment_model_latency.md`

### 2. 스파이크 감지 알고리즘 성능 비교

```bash
python3 benchmarks/run_spike_benchmark.py
```

**기능**:
- Twitter Anomaly Detection, Percentile, Derivative, Z-score 비교
- Precision, Recall, F1-Score 계산
- 실행 시간 측정

**결과**: `spike_algorithm_comparison.md`

### 3. 데이터 저장 성능 벤치마크

```bash
python3 benchmarks/run_storage_benchmark.py
```

**기능**:
- JSONL, Parquet (gzip/snappy), CSV 형식 비교
- 저장/읽기 속도 측정
- 파일 크기 및 압축률 계산

**결과**: `storage_performance.md`

## 벤치마크 실행 전 준비사항

1. **의존성 설치**:
```bash
pip install -r requirements.txt
```

2. **환경 변수 설정** (필요 시):
```bash
export CUDA_VISIBLE_DEVICES=0  # GPU 사용 시
```

3. **모델 다운로드**:
- 첫 실행 시 HuggingFace 모델이 자동으로 다운로드됩니다.

## 벤치마크 결과 해석

### 감정 분석 모델
- **낮은 Latency**: 실시간 처리에 적합
- **P95 Latency**: 95%의 요청이 이 시간 내에 완료됨

### 스파이크 감지 알고리즘
- **Precision**: 감지된 것 중 실제 스파이크 비율
- **Recall**: 실제 스파이크 중 감지된 비율
- **F1-Score**: Precision과 Recall의 조화 평균

### 저장 성능
- **압축률**: 원본 대비 파일 크기 감소율
- **읽기 속도**: 분석 작업에 중요
- **쓰기 속도**: 실시간 저장에 중요

## 주의사항

- 벤치마크 실행 시간은 시스템 성능에 따라 다를 수 있습니다.
- GPU 사용 시 CPU 모드보다 빠른 결과를 얻을 수 있습니다.
- 실제 프로덕션 환경에서는 더 많은 샘플로 테스트하는 것을 권장합니다.

## 결과 업데이트

벤치마크 실행 후 결과를 문서에 반영하려면:

1. 벤치마크 스크립트 실행
2. 결과 확인
3. 해당 `.md` 파일 업데이트

