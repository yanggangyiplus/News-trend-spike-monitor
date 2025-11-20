"""
다크/라이트 모드 색상 유틸리티
"""

import streamlit as st
from typing import Dict, Tuple


def get_theme_colors() -> Dict[str, str]:
    """
    현재 테마에 맞는 색상 반환
    
    Returns:
        색상 딕셔너리 (bg_color, text_color, grid_color 등)
    """
    try:
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"
    except:
        is_dark = False
    
    if is_dark:
        return {
            "bg_color": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "text_color": "white",
            "grid_color": "rgba(255,255,255,0.1)",
            "plot_bgcolor": "rgba(0,0,0,0)",
        }
    else:
        return {
            "bg_color": "white",
            "paper_bgcolor": "white",
            "text_color": "black",
            "grid_color": "rgba(0,0,0,0.1)",
            "plot_bgcolor": "white",
        }


def get_sentiment_color(sentiment_score: float) -> Tuple[str, str]:
    """
    감정 점수에 따른 색상 반환
    
    Args:
        sentiment_score: 감정 점수 (0.0 ~ 1.0)
        
    Returns:
        (배경색, 이모지) 튜플
    """
    if sentiment_score > 0.7:
        return ("#90EE90", "🟢")  # 연한 초록
    elif sentiment_score < 0.3:
        return ("#FFB6C1", "🔴")  # 연한 빨강
    else:
        return ("#FFFFE0", "🟡")  # 연한 노랑


def get_spike_color(score: float, is_top_5: bool = False) -> Tuple[str, str, int]:
    """
    스파이크 점수에 따른 색상 반환
    
    Args:
        score: 스파이크 점수
        is_top_5: 상위 5개 여부
        
    Returns:
        (색상, 테두리 색상, 테두리 두께) 튜플
    """
    if is_top_5:
        if score > 3.0:
            return ("darkred", "black", 3)
        elif score > 2.5:
            return ("darkorange", "black", 3)
        else:
            return ("gold", "black", 3)
    else:
        if score > 3.0:
            return ("red", "white", 1)
        elif score > 2.5:
            return ("orange", "white", 1)
        else:
            return ("yellow", "white", 1)

