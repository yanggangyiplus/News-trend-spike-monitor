"""
사이드바 레이아웃 컴포넌트
"""

import streamlit as st
from dataclasses import dataclass


@dataclass
class SidebarState:
    """사이드바 상태 클래스"""
    keyword: str
    max_results: int
    time_window: int
    should_analyze: bool
    should_refresh: bool
    auto_refresh: bool
    smoothing: bool
    api_url: str


def render_sidebar() -> SidebarState:
    """
    사이드바 렌더링 및 상태 반환
    
    Returns:
        SidebarState 객체
    """
    st.header("⚙️ 설정")
    
    # API URL 설정 (세션 상태에 저장)
    if "api_url" not in st.session_state:
        st.session_state.api_url = "http://localhost:8000"
    
    api_url_input = st.text_input(
        "API 서버 URL",
        value=st.session_state.api_url,
        help="FastAPI 서버 주소를 입력하세요",
    )
    st.session_state.api_url = api_url_input
    
    keyword = st.text_input(
        "키워드",
        value="AI",
        help="분석할 키워드를 입력하세요",
    )
    
    max_results = st.slider(
        "최대 수집 뉴스 개수",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
    )
    
    time_window = st.selectbox(
        "시간 윈도우",
        options=[1, 6, 12, 24, 48],
        index=3,
        format_func=lambda x: f"{x}시간",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        analyze_button = st.button("🔍 분석 시작", type="primary", use_container_width=True)
    with col2:
        refresh_button = st.button("🔄 새로고침", use_container_width=True)
    
    st.divider()
    
    # 자동 새로고침 설정
    auto_refresh = st.checkbox(
        "자동 새로고침 (30초)",
        value=st.session_state.get("auto_refresh", False),
    )
    st.session_state.auto_refresh = auto_refresh
    
    if auto_refresh:
        st.info("30초마다 자동으로 새로고침됩니다")
    
    st.divider()
    
    # 차트 옵션
    st.subheader("📊 차트 옵션")
    smoothing = st.checkbox(
        "스무딩 적용",
        value=st.session_state.get("smoothing", False),
        help="이동 평균을 사용하여 차트를 부드럽게 표시",
    )
    st.session_state.smoothing = smoothing
    
    return SidebarState(
        keyword=keyword,
        max_results=max_results,
        time_window=time_window,
        should_analyze=analyze_button,
        should_refresh=refresh_button,
        auto_refresh=auto_refresh,
        smoothing=smoothing,
        api_url=api_url_input,
    )

