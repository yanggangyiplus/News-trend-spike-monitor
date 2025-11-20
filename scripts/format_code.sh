#!/bin/bash

# 코드 포맷팅 스크립트
# black + isort + flake8

set -e

echo "Running code formatters..."

# Black 포맷팅
echo "Running black..."
black --line-length 100 src app scripts tests

# isort 정렬
echo "Running isort..."
isort --profile black --line-length 100 src app scripts tests

# flake8 검사
echo "Running flake8..."
flake8 src app scripts tests --max-line-length=100 --exclude=venv,.venv,build,dist

echo "Code formatting complete!"

