"""
Alert Rules 탭 컴포넌트
"""

import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def display_alert_rules():
    """
    Alert Rules 탭 표시
    """
    st.subheader("⚙️ 알림 규칙 설정")
    
    st.info("알림 규칙을 설정하여 특정 조건에서 알림을 받을 수 있습니다.")
    
    # 알림 규칙 설정
    with st.form("alert_rule_form"):
        st.subheader("새 알림 규칙 추가")
        
        rule_name = st.text_input("규칙 이름", value="스파이크 감지")
        metric_type = st.selectbox(
            "메트릭 타입",
            options=["스파이크 점수", "감정 점수", "이상치 개수", "API 응답 시간"],
        )
        threshold = st.number_input("임계값", min_value=0.0, value=3.0, step=0.1)
        comparison = st.selectbox(
            "비교 연산자",
            options=[">", ">=", "<", "<=", "=="],
        )
        
        submitted = st.form_submit_button("규칙 추가")
        
        if submitted:
            st.success(f"알림 규칙 '{rule_name}'이 추가되었습니다.")
    
    # 기존 규칙 목록
    st.subheader("현재 알림 규칙")
    
    rules_df = pd.DataFrame([
        {
            "규칙 이름": "스파이크 감지",
            "메트릭": "스파이크 점수",
            "조건": "> 3.0",
            "상태": "활성",
        },
        {
            "규칙 이름": "API 응답 시간",
            "메트릭": "API 응답 시간",
            "조건": "> 5.0",
            "상태": "활성",
        },
    ])
    
    st.dataframe(rules_df, use_container_width=True)
    
    # 알림 규칙 통계
    st.subheader("알림 규칙 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("활성 규칙", "2")
    
    with col2:
        st.metric("오늘 트리거된 알림", "5")
    
    with col3:
        st.metric("마지막 알림", "2분 전")

