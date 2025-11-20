#!/bin/bash

# FastAPI 서버 실행 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${GREEN}Starting FastAPI server...${NC}"

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Python 경로 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# 설정 파일 확인
if [ ! -f "configs/config_api.yaml" ]; then
    echo -e "${YELLOW}Warning: configs/config_api.yaml not found${NC}"
fi

# FastAPI 서버 실행
echo -e "${GREEN}Running FastAPI server on http://0.0.0.0:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo ""

uvicorn app.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
