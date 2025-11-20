"""
Storage 탭 컴포넌트
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

from src.utils.storage import DataStorage

logger = logging.getLogger(__name__)


def display_storage():
    """
    Storage 탭 표시
    """
    st.subheader("💾 데이터 저장소 상태")
    
    try:
        storage = DataStorage()
        
        # 파일 크기 확인
        import os
        
        files_info = []
        for file_path in [
            storage.raw_path,
            storage.clean_path,
            storage.sentiment_path,
            storage.spikes_path,
        ]:
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                files_info.append({
                    "파일": file_path.name,
                    "경로": str(file_path),
                    "크기 (MB)": f"{size_mb:.2f}",
                })
            else:
                files_info.append({
                    "파일": file_path.name,
                    "경로": str(file_path),
                    "크기 (MB)": "0.00",
                })
        
        df = pd.DataFrame(files_info)
        st.dataframe(df, use_container_width=True)
        
        # 데이터 증가량 그래프
        st.subheader("데이터 증가량 추이")
        
        # 샘플 데이터 (실제로는 시간별 데이터 사용)
        dates = pd.date_range(end=datetime.now(), periods=7, freq="D")
        growth_data = pd.DataFrame({
            "날짜": dates,
            "뉴스 개수": [100, 150, 200, 180, 220, 250, 280],
            "감정 분석 개수": [80, 120, 150, 140, 180, 200, 230],
        })
        
        fig = px.line(
            growth_data,
            x="날짜",
            y=["뉴스 개수", "감정 분석 개수"],
            title="데이터 증가량 추이 (7일)",
            labels={"value": "개수", "variable": "데이터 타입"},
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"저장소 정보 조회 오류: {e}")
        st.error(f"저장소 정보 조회 오류: {e}")

