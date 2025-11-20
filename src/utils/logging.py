"""
공통 로깅 유틸리티
로깅 레벨 체계 및 포맷 통일
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포맷터"""
    
    # ANSI 색상 코드
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드 포맷팅"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    use_color: bool = True,
) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (None이면 콘솔만 출력)
        level: 로깅 레벨
        format_string: 커스텀 포맷 문자열
        use_color: 컬러 출력 사용 여부
        
    Returns:
        설정된 로거 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 중복 핸들러 방지
    if logger.handlers:
        return logger
    
    # 기본 포맷 설정
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # 포맷터 생성
    if use_color and sys.stdout.isatty():
        formatter = ColoredFormatter(format_string)
    else:
        formatter = logging.Formatter(format_string)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        # 파일에는 컬러 없이 저장
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    기존 로거를 가져오거나 새로 생성합니다.
    
    Args:
        name: 로거 이름
        
    Returns:
        로거 객체
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


def log_function_call(logger: logging.Logger):
    """
    함수 호출을 로깅하는 데코레이터
    
    Args:
        logger: 로거 객체
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger):
    """
    실행 시간을 로깅하는 데코레이터
    
    Args:
        logger: 로거 객체
        
    Returns:
        데코레이터 함수
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.info(f"Starting {func.__name__}")
            try:
                result = func(*args, **kwargs)
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}", exc_info=True)
                raise
        return wrapper
    return decorator

