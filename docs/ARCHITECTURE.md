# 시스템 아키텍처

## 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    News Trend Monitor                       │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Streamlit   │    │   FastAPI     │    │  Scheduler    │ │
│  │   (Web UI)    │◄───┤   (API)       │◄───┤  (Data Collect)│ │
│  │   Port:8501   │    │   Port:8000   │    │               │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬────────┘ │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                              │                               │
│                    ┌─────────▼─────────┐                    │
│                    │      Redis         │                    │
│                    │    (Cache)         │                    │
│                    │    Port:6379       │                    │
│                    └────────────────────┘                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Storage Layer                      │  │
│  │  - news_raw.jsonl / news_clean.jsonl                │  │
│  │  - sentiment.parquet / spikes.parquet               │  │
│  │  - S3 (Optional)                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         External Data Sources                         │  │
│  │  - RSS Feeds (CNN, BBC, 연합뉴스 등)                  │  │
│  │  - Google News API                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 데이터 플로우

1. **데이터 수집**: RSS 피드 및 Google News API
2. **전처리**: 텍스트 정제, 중복 제거
3. **감정 분석**: HuggingFace Transformers (KcELECTRA)
4. **스파이크 감지**: Twitter Anomaly Detection Algorithm
5. **이상치 탐지**: Z-score, ESD, Moving Average
6. **시각화**: Streamlit 대시보드

## 기술 스택

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Streamlit
- **NLP**: HuggingFace Transformers
- **데이터 처리**: Pandas, NumPy
- **시각화**: Plotly
- **캐싱**: Redis (선택적)
- **배포**: Docker, Kubernetes

## 모듈 구조

- `src/data/`: 데이터 수집 및 전처리
- `src/nlp/`: 감정 분석
- `src/anomaly/`: 이상치 및 스파이크 감지
- `src/services/`: 비즈니스 로직
- `app/api/`: FastAPI 엔드포인트
- `app/web/`: Streamlit 대시보드

