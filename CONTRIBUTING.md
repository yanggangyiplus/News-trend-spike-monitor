# 기여 가이드

## 개발 환경 설정

1. 저장소 클론
2. 가상환경 생성 및 활성화
3. 의존성 설치: `pip install -r requirements.txt`
4. 개발 의존성 설치: `pip install -r requirements-dev.txt` (있는 경우)

## 코드 스타일

- **포맷팅**: black (line-length=100)
- **Import 정렬**: isort (profile=black)
- **Linting**: flake8
- **타입 체크**: mypy

코드 포맷팅:
```bash
bash scripts/format_code.sh
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html
```

## 커밋 메시지

- 명확하고 간결하게 작성
- 변경 사항을 설명하는 제목 사용
- 필요시 상세 설명 추가

## Pull Request

1. 기능 브랜치 생성
2. 변경 사항 커밋
3. 테스트 통과 확인
4. Pull Request 생성

