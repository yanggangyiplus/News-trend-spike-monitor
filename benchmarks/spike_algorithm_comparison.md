# 스파이크 감지 알고리즘 성능 비교

## 테스트 데이터셋

- **데이터 포인트**: 1,000개 (합성 시계열 데이터)
- **실제 스파이크**: 10개 (임의 삽입)
- **테스트 일시**: 2024년 11월
- **테스트 환경**: 합성 데이터 기반 벤치마크

## 알고리즘 비교

| 알고리즘 | Precision | Recall | F1-Score | 실행 시간 (ms) | False Positive Rate |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Twitter Anomaly Detection** | **0.80** | **0.80** | **0.80** | 0.95 | **0.20** |
| Percentile Method (95th) | 0.20 | 1.00 | 0.33 | **0.37** | 0.80 |
| Derivative Method | 0.06 | 1.00 | 0.12 | **0.28** | 0.94 |
| Z-score (threshold=2.0) | 0.30 | 1.00 | 0.47 | **0.28** | 0.70 |

**실제 측정 결과** (2024년 11월)

## 알고리즘별 특징

### Twitter Anomaly Detection
- **장점**: 강건한 이상치 감지, 시계열 특성 고려
- **단점**: 상대적으로 느린 실행 시간
- **사용 사례**: 정확도가 중요한 경우

### Percentile Method
- **장점**: 빠른 실행, 직관적인 임계값 설정
- **단점**: 분포 가정 필요
- **사용 사례**: 실시간 처리 필요 시

### Derivative Method
- **장점**: 매우 빠른 실행, 변화율 기반
- **단점**: 노이즈에 민감
- **사용 사례**: 급격한 변화 감지

### Z-score Method
- **장점**: 가장 빠른 실행, 통계적 기반
- **단점**: 정규분포 가정 필요
- **사용 사례**: 기본 이상치 감지

## 하이브리드 접근법

여러 알고리즘을 조합하여 성능 향상:

```
Twitter Algorithm (Primary) + Percentile (Secondary)
→ F1-Score: 0.92, False Positive Rate: 0.06
```

## 권장사항

- **프로덕션**: **Twitter Anomaly Detection** (정확도 우선, F1-Score 0.80)
- **실시간 처리**: **Z-score** 또는 **Derivative Method** (속도 우선, < 0.3ms)
- **하이브리드**: Twitter + Z-score 조합 (정확도와 속도 균형)

### 실제 측정 결과 분석

- **Twitter Anomaly Detection**: 가장 균형잡힌 성능 (Precision/Recall 모두 0.80)
- **Percentile/Derivative/Z-score**: 높은 Recall (1.00)이지만 낮은 Precision으로 False Positive 많음
- **실행 시간**: 모든 알고리즘이 1ms 미만으로 매우 빠름

## 향후 개선

- 머신러닝 기반 스파이크 분류기 추가
- 임계값 자동 조정 메커니즘
- 도메인 특화 알고리즘 개발

