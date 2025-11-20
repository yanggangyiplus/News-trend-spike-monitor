"""
Log Viewer 탭 컴포넌트
"""

import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def display_log_viewer():
    """
    Log Viewer 탭 표시
    """
    st.subheader("📋 로그 뷰어")
    
    # 로그 레벨 필터
    col1, col2 = st.columns(2)
    
    with col1:
        log_level = st.selectbox(
            "로그 레벨",
            options=["ALL", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=0,
        )
    
    with col2:
        log_file = st.selectbox(
            "로그 파일",
            options=["app.log", "api.log", "scheduler.log"],
            index=0,
        )
    
    # 로그 파일 읽기
    log_path = Path(f"logs/{log_file}")
    
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.readlines()
            
            # 필터링
            if log_level != "ALL":
                logs = [log for log in logs if f" - {log_level} - " in log]
            
            # 최근 로그만 표시
            logs = logs[-100:] if len(logs) > 100 else logs
            
            st.text_area(
                "로그 내용",
                value="".join(logs),
                height=500,
                help="최근 100개 로그만 표시됩니다",
            )
        except Exception as e:
            logger.error(f"로그 파일 읽기 오류: {e}")
            st.error(f"로그 파일 읽기 오류: {e}")
    else:
        st.info(f"로그 파일이 없습니다: {log_path}")

