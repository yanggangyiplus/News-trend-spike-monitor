# API 문서

## 엔드포인트 목록

### Health Check

```
GET /health
```

서비스 상태 확인

**응답:**
```json
{
  "status": "healthy",
  "service": "news-trend-monitor",
  "timestamp": "2025-11-20T20:34:53.384992"
}
```

### 트렌드 분석

```
GET /analyze?keyword=AI&max_results=100&time_window_hours=24
POST /analyze
```

키워드 트렌드 분석 (캐싱 적용, TTL 10분)

**파라미터:**
- `keyword` (필수): 분석할 키워드
- `max_results` (선택): 최대 수집 뉴스 개수 (기본값: 100)
- `time_window_hours` (선택): 시간 윈도우 (기본값: 24)

**응답:**
```json
{
  "keyword": "AI",
  "total_news": 50,
  "avg_sentiment": 0.65,
  "spikes": [...],
  "anomalies": {...},
  "time_series": [...]
}
```

### 비동기 분석

```
POST /analyze/async
```

비동기 분석 작업 생성 (Background Job)

**응답:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "분석 작업이 시작되었습니다."
}
```

### 작업 결과 조회

```
GET /result/{job_id}
```

비동기 작업 결과 조회

### 최근 데이터 조회

```
GET /latest?hours=1
```

최근 N시간 데이터 조회 (Throttling: 1초 간격)

### 감정 분석

```
GET /sentiment?text=이것은 긍정적인 뉴스입니다
```

텍스트 감정 분석

### 메트릭

```
GET /metrics
```

Prometheus 포맷 메트릭

### 스파이크 조회

```
GET /spikes?limit=10
```

스파이크 목록 조회

## 인증

현재 버전에서는 인증이 필요하지 않습니다.

## Rate Limiting

- `/latest`: 1초 간격 제한
- `/analyze`: 캐싱 적용 (TTL 10분)

