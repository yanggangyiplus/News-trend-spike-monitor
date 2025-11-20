"""
감정 트렌드 차트 컴포넌트
스무딩, Rolling Average, Heatmap 포함
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict
import logging

from app.web.components.theme import get_theme_colors

logger = logging.getLogger(__name__)


def display_sentiment_trend(result: Dict, smoothing: bool = False):
    """
    실시간 감정 변화 차트 표시
    
    Args:
        result: 분석 결과 딕셔너리
        smoothing: 스무딩 적용 여부
    """
    time_series = result.get("time_series", [])
    
    if not time_series:
        st.warning("시계열 데이터가 없습니다")
        return
    
    df = pd.DataFrame(time_series)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # 스무딩 적용
    if smoothing and len(df) > 3:
        window_size = min(5, len(df) // 2)
        if window_size >= 3:
            df["avg_sentiment_smooth"] = df["avg_sentiment"].rolling(
                window=window_size, center=True
            ).mean()
            df["avg_sentiment_smooth"] = df["avg_sentiment_smooth"].fillna(df["avg_sentiment"])
        else:
            df["avg_sentiment_smooth"] = df["avg_sentiment"]
    else:
        df["avg_sentiment_smooth"] = df["avg_sentiment"]
    
    # 스파이크 마커
    spikes = result.get("spikes", [])
    spike_indices = [spike["start"] for spike in spikes if spike["start"] < len(df)]
    
    # 이상치 마커
    anomalies = result.get("anomalies", {})
    zscore_indices = [a["start"] for a in anomalies.get("zscore", []) if a["start"] < len(df)]
    moving_avg_indices = [a["start"] for a in anomalies.get("moving_average", []) if a["start"] < len(df)]
    
    # 테마 색상 가져오기
    colors = get_theme_colors()
    
    # 메인 라인 차트 생성
    fig = go.Figure()
    
    # 메인 라인 (스무딩 적용 시)
    if smoothing:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["avg_sentiment"],
            mode="lines",
            name="감정 점수 (원본)",
            line=dict(color="lightblue", width=1, dash="dot"),
            opacity=0.5,
            hovertemplate="<b>시간:</b> %{x}<br><b>감정 점수:</b> %{y:.3f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["avg_sentiment_smooth"],
            mode="lines+markers",
            name="감정 점수 (스무딩)",
            line=dict(color="blue", width=2),
            marker=dict(size=6, color="blue"),
            hovertemplate="<b>시간:</b> %{x}<br><b>감정 점수:</b> %{y:.3f}<extra></extra>",
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["avg_sentiment"],
            mode="lines+markers",
            name="감정 점수",
            line=dict(color="blue", width=2),
            marker=dict(size=6, color="blue"),
            hovertemplate="<b>시간:</b> %{x}<br><b>감정 점수:</b> %{y:.3f}<extra></extra>",
        ))
    
    # 이상치 구간 강조 (Highlight 영역)
    if zscore_indices or moving_avg_indices:
        all_anomaly_indices = sorted(set(zscore_indices + moving_avg_indices))
        for idx in all_anomaly_indices:
            if idx < len(df):
                fig.add_vrect(
                    x0=df.iloc[max(0, idx-1)]["timestamp"],
                    x1=df.iloc[min(len(df)-1, idx+1)]["timestamp"],
                    fillcolor="rgba(255, 165, 0, 0.2)",
                    layer="below",
                    line_width=0,
                )
    
    # 스파이크 표시
    if spike_indices:
        spike_df = df.iloc[spike_indices]
        
        fig.add_trace(go.Scatter(
            x=spike_df["timestamp"],
            y=spike_df["avg_sentiment"],
            mode="markers",
            name="스파이크",
            marker=dict(
                size=15,
                color="red",
                symbol="diamond",
                line=dict(width=2, color="darkred"),
            ),
            hovertemplate="<b>스파이크</b><br>시간: %{x}<br>값: %{y:.3f}<extra></extra>",
        ))
    
    # 이상치 표시 (Z-score)
    if zscore_indices:
        zscore_df = df.iloc[zscore_indices]
        fig.add_trace(go.Scatter(
            x=zscore_df["timestamp"],
            y=zscore_df["avg_sentiment"],
            mode="markers",
            name="이상치 (Z-score)",
            marker=dict(
                size=12,
                color="orange",
                symbol="x",
                line=dict(width=2, color="darkorange"),
            ),
            hovertemplate="<b>이상치 (Z-score)</b><br>시간: %{x}<br>값: %{y:.3f}<extra></extra>",
        ))
    
    # 이상치 표시 (Moving Average)
    if moving_avg_indices:
        moving_avg_df = df.iloc[moving_avg_indices]
        fig.add_trace(go.Scatter(
            x=moving_avg_df["timestamp"],
            y=moving_avg_df["avg_sentiment"],
            mode="markers",
            name="이상치 (Moving Avg)",
            marker=dict(
                size=12,
                color="purple",
                symbol="square",
                line=dict(width=2, color="darkviolet"),
            ),
            hovertemplate="<b>이상치 (Moving Avg)</b><br>시간: %{x}<br>값: %{y:.3f}<extra></extra>",
        ))
    
    # 레이아웃 설정
    fig.update_layout(
        title=f"'{result.get('keyword', '')}' 키워드 감정 트렌드",
        xaxis_title="시간",
        yaxis_title="감정 점수 (0=부정, 1=긍정)",
        hovermode="x unified",
        height=500,
        plot_bgcolor=colors["plot_bgcolor"],
        paper_bgcolor=colors["paper_bgcolor"],
        font=dict(color=colors["text_color"]),
        xaxis=dict(gridcolor=colors["grid_color"]),
        yaxis=dict(gridcolor=colors["grid_color"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor=colors["bg_color"],
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stacked Bar Chart 추가
    st.subheader("📊 긍정/부정 비중")
    if len(df) > 0:
        df["positive_ratio"] = df["avg_sentiment"]
        df["negative_ratio"] = 1 - df["avg_sentiment"]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df["timestamp"],
            y=df["positive_ratio"],
            name="긍정",
            marker_color="green",
            hovertemplate="<b>시간:</b> %{x}<br><b>긍정 비율:</b> %{y:.2%}<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            x=df["timestamp"],
            y=df["negative_ratio"],
            name="부정",
            marker_color="red",
            hovertemplate="<b>시간:</b> %{x}<br><b>부정 비율:</b> %{y:.2%}<extra></extra>",
        ))
        
        fig_bar.update_layout(
            barmode="stack",
            height=300,
            plot_bgcolor=colors["plot_bgcolor"],
            paper_bgcolor=colors["paper_bgcolor"],
            font=dict(color=colors["text_color"]),
            xaxis=dict(gridcolor=colors["grid_color"]),
            yaxis=dict(gridcolor=colors["grid_color"], tickformat=".0%"),
            legend=dict(bgcolor=colors["bg_color"]),
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 7일 Rolling Average 추가
    if len(df) > 1:
        st.subheader("📊 7일 Rolling Average")
        df["rolling_avg"] = df["avg_sentiment"].rolling(
            window=min(7, len(df)), center=True
        ).mean()
        
        fig_rolling = go.Figure()
        fig_rolling.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["avg_sentiment"],
            mode="lines",
            name="원본",
            line=dict(color="lightblue", width=1),
            opacity=0.5,
        ))
        fig_rolling.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["rolling_avg"],
            mode="lines",
            name="7일 Rolling Average",
            line=dict(color="blue", width=2),
        ))
        
        fig_rolling.update_layout(
            title="7일 Rolling Average",
            xaxis_title="시간",
            yaxis_title="감정 점수",
            height=300,
            plot_bgcolor=colors["plot_bgcolor"],
            paper_bgcolor=colors["paper_bgcolor"],
            font=dict(color=colors["text_color"]),
        )
        
        st.plotly_chart(fig_rolling, use_container_width=True)
    
    # 스파이크 Heatmap 추가
    if spikes:
        st.subheader("🔥 스파이크 Heatmap")
        
        spike_df = pd.DataFrame(spikes)
        spike_df["timestamp"] = pd.to_datetime(spike_df["timestamp"])
        spike_df["hour"] = spike_df["timestamp"].dt.hour
        spike_df["day"] = spike_df["timestamp"].dt.day
        
        # Heatmap 데이터 생성
        heatmap_data = spike_df.groupby(["day", "hour"])["score"].mean().unstack(fill_value=0)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale="Reds",
            colorbar=dict(title="스파이크 점수"),
        ))
        
        fig_heatmap.update_layout(
            title="스파이크 Heatmap (일별 × 시간별)",
            xaxis_title="시간 (시)",
            yaxis_title="일",
            height=400,
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 통계 정보
    if len(df) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("최소 감정 점수", f"{df['avg_sentiment'].min():.3f}")
        with col2:
            st.metric("최대 감정 점수", f"{df['avg_sentiment'].max():.3f}")
        with col3:
            st.metric("표준편차", f"{df['avg_sentiment'].std():.3f}")

