"""
설정 파일 로더
YAML 설정 파일을 로드하고 검증하는 유틸리티
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    YAML 설정 파일을 로드합니다.
    
    Args:
        config_path: 설정 파일 경로
        
    Returns:
        설정 딕셔너리
        
    Raises:
        FileNotFoundError: 설정 파일이 존재하지 않을 때
        yaml.YAMLError: YAML 파싱 오류 시
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"설정 파일 로드 완료: {config_path}")
        return config
    
    except yaml.YAMLError as e:
        logger.error(f"YAML 파싱 오류: {e}")
        raise


def get_project_root() -> Path:
    """
    프로젝트 루트 디렉토리 경로를 반환합니다.
    
    Returns:
        프로젝트 루트 Path 객체
    """
    return Path(__file__).parent.parent.parent

