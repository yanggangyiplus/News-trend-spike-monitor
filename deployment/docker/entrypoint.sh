#!/bin/bash
# 공통 엔트리포인트 스크립트
# 권한 처리 및 환경 설정

set -e

# Python 경로 설정
export PYTHONPATH=/app:$PYTHONPATH

# 로그 디렉토리 생성
mkdir -p /app/logs
mkdir -p /app/data/processed
mkdir -p /app/data/raw

# 권한 설정
chmod -R 755 /app/logs
chmod -R 755 /app/data

# 명령어 실행
exec "$@"

