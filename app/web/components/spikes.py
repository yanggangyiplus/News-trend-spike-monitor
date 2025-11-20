"""
스파이크 구간 차트 컴포넌트
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict
import logging

from app.web.components.theme import get_theme_colors, get_spike_color

logger = logging.getLogger(__name__)


def display_spikes(result: Dict):
    """
    스파이크 구간 차트 표시
    
    Args:
        result: 분석 결과 딕셔너리
    """
    spikes = result.get("spikes", [])
    
    if not spikes:
        st.info("감지된 스파이크가 없습니다")
        return
    
    # 스파이크 데이터프레임 생성 및 정렬
    spike_df = pd.DataFrame(spikes)
    spike_df = spike_df.sort_values("score", ascending=False).reset_index(drop=True)
    
    # 상위 5개 강조 (버그 수정)
    top_5 = set(spike_df.index[:5])
    
    # 테마 색상 가져오기
    colors = get_theme_colors()
    
    # Bar 차트 생성
    fig = go.Figure()
    
    # 스파이크 값에 따라 색상 분기 및 상위 5개 강조
    bar_colors = []
    marker_lines = []
    marker_line_widths = []
    
    for idx in spike_df.index:
        score = spike_df.loc[idx, "score"]
        is_top_5 = idx in top_5
        color, line_color, line_width = get_spike_color(score, is_top_5)
        bar_colors.append(color)
        marker_lines.append(line_color)
        marker_line_widths.append(line_width)
    
    fig.add_trace(go.Bar(
        x=spike_df["timestamp"],
        y=spike_df["score"],
        name="스파이크 점수",
        marker=dict(
            color=bar_colors,
            line=dict(color=marker_lines, width=marker_line_widths),
        ),
        hovertemplate="<b>시간:</b> %{x}<br><b>스파이크 점수:</b> %{y:.3f}<br><b>값:</b> %{customdata:.3f}<extra></extra>",
        customdata=spike_df["value"],
    ))
    
    fig.update_layout(
        title="스파이크 구간 분석 (상위 5개 강조)",
        xaxis_title="시간",
        yaxis_title="스파이크 점수 (Z-score)",
        height=400,
        plot_bgcolor=colors["plot_bgcolor"],
        paper_bgcolor=colors["paper_bgcolor"],
        font=dict(color=colors["text_color"]),
        xaxis=dict(gridcolor=colors["grid_color"]),
        yaxis=dict(gridcolor=colors["grid_color"]),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 스파이크 상세 정보 테이블
    st.subheader("스파이크 상세 정보")
    display_df = spike_df[["timestamp", "value", "score"]].copy()
    display_df.columns = ["시간", "감정 점수", "스파이크 점수"]
    display_df["스파이크 점수"] = display_df["스파이크 점수"].round(3)
    display_df["감정 점수"] = display_df["감정 점수"].round(3)
    st.dataframe(display_df, use_container_width=True)

