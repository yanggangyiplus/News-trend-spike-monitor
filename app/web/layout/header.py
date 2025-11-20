"""
상단 헤더 메트릭 컴포넌트
"""

import streamlit as st
from typing import Dict, Optional


def render_header(result: Optional[Dict] = None):
    """
    상단 헤더 메트릭 렌더링
    
    Args:
        result: 분석 결과 딕셔너리 (None이면 기본 메트릭 표시)
    """
    if result is None:
        st.info("👈 사이드바에서 키워드를 입력하고 '분석 시작' 버튼을 클릭하세요")
        return
    
    # 요약 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 뉴스 개수", result.get("total_news", 0))
    
    with col2:
        avg_sentiment = result.get("avg_sentiment", 0.5)
        st.metric("평균 감정 점수", f"{avg_sentiment:.3f}")
    
    with col3:
        spikes_count = len(result.get("spikes", []))
        st.metric("스파이크 개수", spikes_count)
    
    with col4:
        anomalies = result.get("anomalies", {})
        total_anomalies = len(anomalies.get("zscore", [])) + len(anomalies.get("moving_average", []))
        st.metric("이상치 개수", total_anomalies)
    
    st.divider()

