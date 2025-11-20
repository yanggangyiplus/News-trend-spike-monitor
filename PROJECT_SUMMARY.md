# 프로젝트 요약

## 프로젝트 개요

**News Trend Spike Monitor**는 뉴스 기반 실시간 트렌드 스파이크 모니터링 시스템입니다.

## 핵심 기능

1. **실시간 데이터 수집**: RSS 피드 및 Google News API
2. **감정 분석**: HuggingFace Transformers (KcELECTRA)
3. **스파이크 감지**: Twitter Anomaly Detection Algorithm
4. **이상치 탐지**: Z-score, ESD, Moving Average
5. **실시간 대시보드**: Streamlit 기반 시각화
6. **RESTful API**: FastAPI 기반 데이터 서비스

## 기술 스택

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Streamlit
- **NLP**: HuggingFace Transformers
- **데이터 처리**: Pandas, NumPy, PyArrow
- **시각화**: Plotly
- **배포**: Docker, Kubernetes
- **모니터링**: Prometheus 메트릭

## 프로젝트 통계

- **Python 파일**: 56개
- **테스트 파일**: 8개
- **설정 파일**: 4개
- **문서 파일**: 3개

## 주요 파일

- `app/web/main.py`: Streamlit 메인 대시보드 (201줄)
- `app/api/main.py`: FastAPI 서버
- `src/services/trend_service.py`: 트렌드 분석 통합 서비스
- `scripts/scheduler.py`: 실시간 수집 스케줄러

## 실행 방법

```bash
# Streamlit 대시보드
bash scripts/run_streamlit.sh

# FastAPI 서버
bash scripts/run_api.sh

# Docker Compose
cd deployment/docker && docker-compose up -d
```

## 문서

- [README.md](README.md): 프로젝트 전체 설명
- [docs/QUICK_START.md](docs/QUICK_START.md): 빠른 시작 가이드
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md): API 문서
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): 아키텍처 문서

