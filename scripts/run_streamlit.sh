#!/bin/bash

# Streamlit 대시보드 실행 스크립트

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

echo -e "${GREEN}Starting Streamlit dashboard...${NC}"

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

# Streamlit 설치 확인
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${RED}Error: streamlit not installed${NC}"
    echo -e "${YELLOW}Please install dependencies: pip install -r requirements.txt${NC}"
    exit 1
fi

# 설정 파일 확인
if [ ! -f "configs/config_api.yaml" ]; then
    echo -e "${YELLOW}Warning: configs/config_api.yaml not found${NC}"
fi

# Streamlit 실행
echo -e "${GREEN}Running Streamlit dashboard on http://localhost:8501${NC}"
echo ""

streamlit run app/web/main.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true
