# 빠른 시작 가이드

## 설치

```bash
# 저장소 클론
git clone <repository-url>
cd News-trend-spike-monitor

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 실행

### 1. Streamlit 대시보드 실행

```bash
bash scripts/run_streamlit.sh
# 또는
streamlit run app/web/main.py --server.port 8501
```

브라우저에서 http://localhost:8501 접속

### 2. FastAPI 서버 실행

```bash
bash scripts/run_api.sh
# 또는
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

API 문서: http://localhost:8000/docs

### 3. Docker Compose로 전체 스택 실행

```bash
cd deployment/docker
docker-compose up -d
```

## 사용 방법

1. Streamlit 대시보드에서 키워드 입력 (예: "AI", "Technology")
2. "분석 시작" 버튼 클릭
3. 결과 확인:
   - 실시간 감정 변화 차트
   - 스파이크 구간 분석
   - 뉴스 상세 리스트

## 설정

설정 파일은 `configs/` 디렉토리에 있습니다:
- `config_api.yaml`: API 서버 설정
- `config_collector.yaml`: 데이터 수집 설정
- `config_nlp.yaml`: NLP 모델 설정
- `config_anomaly.yaml`: 이상치/스파이크 감지 설정

