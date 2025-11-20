# 📈 News Trend Spike Monitor

**뉴스 기반 실시간 트렌드 스파이크 모니터링 시스템**

End-to-End AI/ML Engineering 프로젝트로, 뉴스 데이터 수집부터 감정 분석, 스파이크 감지, 실시간 대시보드까지 전체 파이프라인을 구현한 프로덕션 수준의 시스템입니다.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 프로젝트 요약 (3줄)

**이 프로젝트는 뉴스 데이터를 실시간으로 수집·분석하고, 감정 분석 + 시계열 스파이크 탐지를 결합한 End-to-End 시스템입니다.**  
**전체 파이프라인을 직접 설계·구현했고, 실시간 대시보드 운영 수준까지 구현했습니다.**  
**RSS/Google News API 수집 → NLP 감정 분석 → Twitter Anomaly Detection 스파이크 감지 → Streamlit 실시간 시각화까지 완전 자동화된 파이프라인입니다.**

## 핵심 성과 요약

| 항목 | 성과 |
|:---:|:---:|
| **데이터 수집** | RSS 피드 + Google News API 연동 |
| **감정 분석** | HuggingFace Transformers (KcELECTRA), 평균 54ms Latency |
| **스파이크 감지** | Twitter Anomaly Detection Algorithm, F1-Score 0.80 |
| **이상치 탐지** | Z-score, ESD, Moving Average 3가지 방법 |
| **대시보드** | Streamlit 기반 실시간 모니터링 UI |
| **구현 범위** | 수집부터 시각화까지 End-to-End 파이프라인 |

## 핵심 성능 지표

| 항목 | 수치 |
|:---:|:---:|
| **감정 분석 Latency** | 평균 54ms, P95 67.68ms |
| **스파이크 감지 알고리즘 F1-Score** | 0.80 (Twitter Algorithm) |
| **스파이크 감지 실행 시간** | 0.95ms |
| **스케줄러 처리 주기** | 최소 30초 |
| **데이터 저장 압축률** | Parquet (gzip) 93.3% |
| **API 응답 캐싱** | TTL 10분 |

## 프로젝트 미리보기

![대시보드 데모](assets/dashboard_demo.gif)

*Streamlit 대시보드 화면 - 실시간 뉴스 트렌드 모니터링 및 스파이크 감지*

> 💡 **참고**: 실제 이미지는 `assets/` 디렉토리에 추가하세요.

## 문제 정의 & 해결 접근

뉴스 기반 실시간 트렌드 변화(Trend Spike) 감지와 감정 분석·이상치 탐지·시계열 분석을 결합하여 특정 키워드/브랜드/이슈에 대한 실시간 여론·감정 흐름을 모니터링하는 시스템이 필요했습니다.

기존 도구들은 단순 감정 분석에 그치며 시계열 트렌드 분석과 변화점 탐지 기능이 부족했습니다. 이 프로젝트는 실시간 데이터 수집부터 감정 분석, 트렌드 분석, 스파이크 감지까지 End-to-End 파이프라인을 제공합니다.

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 (User)                             │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │     Streamlit Dashboard (Port:8501)     │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │         FastAPI Backend (Port:8000)    │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │     Data Collection Pipeline            │
        │  RSS 피드 / Google News API             │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │      Text Preprocessing                 │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │      Sentiment Analysis                 │
        │  HuggingFace Transformers (KcELECTRA)   │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │    Spike Detection Engine               │
        │  Twitter Algorithm / Percentile / Derivative
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │    Anomaly Detection Engine             │
        │  Z-score / ESD / Moving Average         │
        └─────────────────────────────────────────┘
```

### 데이터 파이프라인

```
Raw News → Collection → Preprocessing → Sentiment Analysis 
→ Time Series → Spike Detection → Anomaly Detection → Visualization
```

## 핵심 기술 스택

| 영역 | 기술 | 선택 이유 |
|------|------|----------|
| **Backend** | FastAPI | 고성능 API 서버, 자동 문서화 |
| **Frontend** | Streamlit | 빠른 프로토타이핑 및 실시간 모니터링 |
| **NLP** | HuggingFace Transformers (KcELECTRA-base) | 한국어 감정 분석 최적화 |
| **이상치 탐지** | Z-score, ESD, Moving Average | 다양한 통계 기반 방법 |
| **스파이크 감지** | Twitter Algorithm, Percentile, Derivative | 실시간 트렌드 변화 감지 |
| **데이터 처리** | Pandas, NumPy | 데이터 처리 및 통계 분석 |
| **시각화** | Plotly | 인터랙티브 차트 |
| **배포** | Docker, Kubernetes | 컨테이너화 및 확장 가능한 아키텍처 |

## 핵심 기술 구현

### NLP 감정 분석

HuggingFace Transformers의 `beomi/KcELECTRA-base` 모델을 사용하여 한국어 뉴스 텍스트의 감정을 분석합니다.

**주요 특징**:
- 다중 모델 지원: KcELECTRA (한국어 최적화), bert-base-multilingual-cased (다국어)
- 자동 디바이스 선택: GPU (CUDA), CPU, MPS (Apple Silicon) 자동 감지
- 배치 처리: 효율적인 배치 처리로 대량 텍스트 분석 지원
- 신뢰도 점수: 각 분석 결과에 대한 confidence 점수 제공

**출력 형식**: `positive`, `negative`, `neutral`, `confidence` (0.0 ~ 1.0)

### 스파이크 감지 알고리즘

**Twitter Anomaly Detection Algorithm (S-H-ESD)**:
- 중앙값(Median)과 MAD(Median Absolute Deviation)를 사용한 강건한 이상치 감지
- 정규분포 가정 없이 동작하여 다양한 분포에 적합
- Z-score 기반 임계값으로 스파이크 구간 탐지

**Percentile Method**: 상위/하위 백분위수 기반 스파이크 감지  
**Derivative Method**: 변화율(미분) 기반 급격한 변화 감지

### 이상치 탐지 알고리즘

- **Z-score Detector**: 표준 편차 기반 이상치 감지 (임계값 2.0)
- **Moving Average Detector**: 이동 평균 대비 편차 기반 이상치 감지
- **ESD (Extreme Studentized Deviate)**: 극값 통계 테스트 기반 이상치 감지

## 실행 방법

### Quick Start

```bash
# 저장소 클론
git clone https://github.com/yanggangyiplus/News-trend-spike-monitor.git
cd News-trend-spike-monitor

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Streamlit 대시보드 실행
streamlit run app/web/main.py --server.port 8501

# 또는 FastAPI 서버 실행
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 설정 파일

- `configs/config_api.yaml`: API 서버 설정
- `configs/config_collector.yaml`: 데이터 수집 설정 (RSS URL, Google News API 키)
- `configs/config_nlp.yaml`: NLP 모델 설정
- `configs/config_anomaly.yaml`: 이상치/스파이크 감지 설정

## 실시간 대시보드

Streamlit 기반 대시보드는 3개의 주요 탭으로 구성:

1. **실시간 감정 변화**: 시계열 감정 점수 추이를 Plotly 기반 인터랙티브 차트로 표시, 스파이크 구간 강조
2. **스파이크 구간**: 감지된 스파이크를 시간순으로 Bar 차트로 표시, 상세 정보 테이블 제공
3. **키워드별 기사 상세 리스트**: 수집된 뉴스 기사를 테이블 형태로 표시, 감정 점수에 따라 색상 분기

**기능**: 자동 새로고침 (30초), 수동 새로고침, 사이드바에서 키워드/최대 결과 수/시간 윈도우 조정

## 성능 벤치마크

- [감정 분석 모델 Latency](benchmarks/sentiment_model_latency.md): KcELECTRA 평균 54.07ms, P95 67.68ms
- [스파이크 알고리즘 비교](benchmarks/spike_algorithm_comparison.md): Twitter Algorithm F1-Score 0.80, 실행 시간 0.95ms
- [저장 성능 벤치마크](benchmarks/storage_performance.md): Parquet (gzip) 압축률 93.3%, 읽기 시간 0.0초

## 확장 가능성 & 최적화

### 확장 가능한 아키텍처
- 모듈화 설계: 단일 책임 원칙에 따른 계층별 모듈 분리
- 설정 기반: YAML 기반 설정 파일로 다양한 환경 대응
- API 우선: FastAPI 기반 RESTful API로 다양한 클라이언트 지원
- 테스트 가능: pytest 기반 테스트 코드로 안정성 보장

### 성능 최적화 전략
- **캐싱**: FastAPI 응답 캐싱 (TTL 10분), Redis 통합 가능
- **비동기 처리**: Background Tasks로 무거운 NLP/스파이크 처리 분리, AsyncIO 활용
- **API 최적화**: `/latest` 엔드포인트 Throttling (1초 간격), Pagination 지원
- **데이터베이스 최적화**: 시간 기반 인덱싱, 배치 처리, Connection Pooling

### 확장 기술 스택
- **데이터 파이프라인**: Apache Kafka (실시간 스트리밍), Apache Airflow (워크플로우 오케스트레이션)
- **모니터링**: Prometheus (메트릭 수집), Grafana (대시보드)
- **ML/AI**: MLflow (모델 버전 관리), Kubeflow (Kubernetes 기반 ML 워크플로우)
- **인프라**: Docker Compose, Kubernetes, CI/CD (GitHub Actions)

## 배포

### Docker Compose

```bash
cd deployment/docker
docker-compose up -d
```

서비스 접속: FastAPI (http://localhost:8000), Streamlit (http://localhost:8501), Redis (localhost:6379)

### Kubernetes

```bash
kubectl create namespace news-trend
kubectl apply -f deployment/k8s/redis-deployment.yaml
kubectl apply -f deployment/k8s/api-deployment.yaml
kubectl apply -f deployment/k8s/web-deployment.yaml
```

### CI/CD

GitHub Actions를 통한 자동화된 CI/CD 파이프라인:
- CI: 코드 포맷팅 검사 (black, isort), 린팅 (flake8), 타입 체크 (mypy), 테스트 실행 (pytest)
- CD: Docker 이미지 빌드 및 DockerHub 자동 푸시

## 한계 & 개선 방향

### 현재 한계
- Google News API 무료 플랜 제한 (하루 100회)
- Fine-tuning 없이 기본 모델 사용
- 배치 처리 기반 (완전한 실시간 스트리밍 미구현)
- 주로 한국어 중심 (다국어 확장 필요)

### 개선 방향
- **v1**: Fine-tuning된 감정 분석 모델 통합, 다국어 지원 확대, SQLite/PostgreSQL 기반 데이터 영구 저장
- **v2**: Apache Kafka를 활용한 실시간 데이터 스트리밍 파이프라인, Twitter/X API 등 추가 소스 연동
- **v3**: Prometheus + Grafana 기반 시스템 모니터링, MLflow 기반 모델 버전 관리, Kubernetes 기반 확장 가능한 아키텍처

## 개인 기여도

이 프로젝트는 **개인 프로젝트**로, 모든 작업을 직접 수행했습니다.

- **엔드투엔드 데이터 파이프라인 설계**: Raw 수집 → 전처리 → 감정 분석 → 시계열 분석 → 스파이크 감지 → UI까지 풀 사이클 개발
- **API 통신·데이터 엔지니어링**: RSS Feedparser, Google News API 연동 및 오류 처리, 재시도 로직 구현
- **한국어 NLP 모델 활용**: HuggingFace Transformers 기반 감정 분석 파이프라인, KcELECTRA 모델 적용, GPU/CPU 자동 선택 로직 구현
- **시계열 분석·스파이크 감지**: Twitter Anomaly Detection Algorithm (S-H-ESD), Percentile Method, Derivative Method 구현
- **이상치 탐지**: Z-score, ESD, Moving Average Deviation 구현
- **데이터 시각화 & UX**: Streamlit 기반 실시간 대시보드, Plotly 기반 인터랙티브 시계열 차트 구현
- **백엔드·서비스 설계**: FastAPI 기반 RESTful API 설계, Swagger UI 자동 문서화

## 프로젝트 구조

```
News-trend-spike-monitor/
├── app/                    # 웹 애플리케이션
│   ├── api/               # FastAPI 서버
│   └── web/               # Streamlit UI
├── src/                   # 소스 코드
│   ├── data/             # 데이터 수집·전처리
│   ├── nlp/              # 감정 분석
│   ├── anomaly/          # 이상치 감지
│   ├── services/         # 비즈니스 로직
│   └── utils/            # 공통 유틸리티
├── configs/              # YAML 설정 파일
├── deployment/           # Docker, Kubernetes 배포 파일
├── benchmarks/           # 성능 벤치마크 문서
├── docs/                 # 문서
├── tests/                # 테스트 코드
└── scripts/              # 실행 스크립트
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 코드 포맷팅
bash scripts/format_code.sh
```

## 면접 질문 대응

### 실시간 분석 관련

**Q: 실시간 데이터 처리를 위해 어떤 기술을 사용했나요?**

**A**: 
- 비동기 처리: AsyncIO를 활용한 비동기 데이터 수집 및 처리
- 스트리밍 파이프라인: RSS 피드와 Google News API를 통한 실시간 데이터 수집
- 스케줄러: 주기적 데이터 수집 (30초/1분/5분 간격)
- 캐싱: Redis를 통한 응답 시간 최적화
- Background Jobs: 무거운 NLP 작업을 백그라운드로 분리

### 스파이크 감지 관련

**Q: 스파이크 감지 알고리즘의 원리와 선택 이유는?**

**A**:
- Twitter Anomaly Detection: 시계열 데이터에 특화된 알고리즘, 중앙값과 MAD를 사용한 강건한 이상치 감지
- Z-score 기반 감지: 통계적 이상치 탐지로 급격한 변화 감지
- Moving Average Deviation: 이동 평균 대비 편차 기반 감지
- 다중 알고리즘 결합: 단일 알고리즘의 한계를 보완하기 위해 여러 방법 조합
- 임계값 조정 가능: 도메인 특성에 맞게 임계값 동적 조정

### 엔지니어링 관련

**Q: 프로젝트의 확장성과 운영 안정성을 어떻게 보장했나요?**

**A**:
- 모듈화 설계: 단일 책임 원칙에 따른 계층별 모듈 분리
- 컨테이너화: Docker 기반 배포로 환경 일관성 보장
- Kubernetes 지원: 확장 가능한 컨테이너 오케스트레이션
- 모니터링: Prometheus 메트릭을 통한 실시간 모니터링
- 로깅: 구조화된 로깅으로 디버깅 및 문제 추적 용이
- 테스트: pytest 기반 테스트 코드로 안정성 보장
- CI/CD: 자동화된 빌드 및 배포 파이프라인

**Q: 대규모 트래픽을 처리하기 위한 전략은?**

**A**:
- 캐싱 전략: Redis를 통한 응답 캐싱 (TTL 10분)
- Throttling: `/latest` 엔드포인트 1초 간격 제한
- Background Processing: 무거운 작업을 비동기로 처리
- Horizontal Scaling: Kubernetes HPA를 통한 자동 스케일링
- 데이터 파이프라인: Kafka 연동 가능 (확장성)
- 배치 처리: NLP 모델 배치 추론으로 처리량 향상

## 상세 문서

- [빠른 시작 가이드](docs/QUICK_START.md)
- [API 문서](docs/API_DOCUMENTATION.md)
- [아키텍처 문서](docs/ARCHITECTURE.md)
- [벤치마크 실행 가이드](benchmarks/README.md)

## 라이선스 & 작성자

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

**작성자**: yanggangyi

- GitHub: [@yanggangyiplus](https://github.com/yanggangyiplus)
