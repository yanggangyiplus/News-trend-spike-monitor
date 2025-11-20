"""
Streamlit 메인 대시보드
실시간 트렌드 모니터링 UI
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import logging
from typing import Optional, Dict

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.services.trend_service import TrendService

# 레이아웃 컴포넌트
from app.web.layout.sidebar import render_sidebar, SidebarState
from app.web.layout.header import render_header

# UI 컴포넌트
from app.web.components.sentiment_trend import display_sentiment_trend
from app.web.components.spikes import display_spikes
from app.web.components.news_list import display_news_list
from app.web.components.metrics_tab import display_metrics
from app.web.components.storage_tab import display_storage
from app.web.components.log_viewer_tab import display_log_viewer
from app.web.components.alert_rules_tab import display_alert_rules

# 페이지 설정
st.set_page_config(
    page_title="News Trend Spike Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 로거 설정
logger = setup_logger("web", level=logging.INFO)

# 전역 변수 초기화
if "trend_service" not in st.session_state:
    try:
        config = load_config("configs/config_api.yaml")
        st.session_state.trend_service = TrendService(config_path="configs/config_api.yaml")
    except Exception as e:
        logger.warning(f"설정 파일 로드 실패, 기본 설정 사용: {e}")
        st.session_state.trend_service = TrendService()

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

if "smoothing" not in st.session_state:
    st.session_state.smoothing = False

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False


def run_analysis(
    keyword: str,
    max_results: int,
    time_window_hours: int,
) -> Optional[Dict]:
    """
    트렌드 분석 실행
    
    Args:
        keyword: 분석할 키워드
        max_results: 최대 수집 뉴스 개수
        time_window_hours: 시간 윈도우
        
    Returns:
        분석 결과 딕셔너리 또는 None
    """
    try:
        result = st.session_state.trend_service.analyze_trend(
            keyword=keyword,
            max_results=max_results,
            time_window_hours=time_window_hours,
        )
        logger.info(f"분석 완료: {keyword}")
        return result
    except Exception as e:
        logger.error(f"분석 오류: {e}")
        st.error(f"분석 중 오류 발생: {e}")
        return None


def show_loading_skeleton():
    """로딩 중 skeleton UI 표시"""
    st.info("🔄 데이터를 불러오는 중...")
    with st.container():
        st.empty()
        st.progress(0.5)
        st.empty()


def main():
    """메인 대시보드 함수"""
    st.title("📈 News Trend Spike Monitor")
    st.markdown("뉴스 기반 실시간 트렌드 변화 및 감정 분석 대시보드")
    
    # 사이드바 렌더링
    with st.sidebar:
        sidebar_state = render_sidebar()
    
    # 분석 실행
    if sidebar_state.should_analyze or sidebar_state.should_refresh:
        st.session_state.is_loading = True
        with st.spinner("분석 중..."):
            result = run_analysis(
                keyword=sidebar_state.keyword,
                max_results=sidebar_state.max_results,
                time_window_hours=sidebar_state.time_window,
            )
            if result:
                st.session_state.analysis_result = result
                st.session_state.analysis_keyword = sidebar_state.keyword
            st.session_state.is_loading = False
    
    # 자동 새로고침 처리 (st_autorefresh 사용)
    if sidebar_state.auto_refresh and st.session_state.analysis_result:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=30000, key="auto_refresh")  # 30초
        except ImportError:
            # streamlit-autorefresh가 없으면 일반 새로고침 사용 (성능 개선)
            import time
            if "last_refresh" not in st.session_state:
                st.session_state.last_refresh = time.time()
            
            current_time = time.time()
            if current_time - st.session_state.last_refresh >= 30:
                st.session_state.last_refresh = current_time
                st.rerun()
    
    # 로딩 상태 표시
    if st.session_state.is_loading:
        show_loading_skeleton()
    
    # 헤더 렌더링
    render_header(st.session_state.analysis_result)
    
    # 결과가 없으면 안내 메시지 표시
    if not st.session_state.analysis_result:
        st.info("👈 사이드바에서 키워드를 입력하고 '분석 시작' 버튼을 클릭하세요")
        return
    
    result = st.session_state.analysis_result
    
    # 탭 구성
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 실시간 감정 변화",
        "🚨 스파이크 구간",
        "📰 키워드별 기사 상세",
        "📈 Metrics",
        "💾 Storage",
        "📋 Log Viewer",
        "⚙️ Alert Rules",
    ])
    
    # 탭 1: 실시간 감정 변화
    with tab1:
        display_sentiment_trend(result, smoothing=sidebar_state.smoothing)
    
    # 탭 2: 스파이크 구간
    with tab2:
        display_spikes(result)
    
    # 탭 3: 키워드별 기사 상세
    with tab3:
        display_news_list(result)
    
    # 탭 4: Metrics
    with tab4:
        display_metrics(api_url=sidebar_state.api_url)
    
    # 탭 5: Storage
    with tab5:
        display_storage()
    
    # 탭 6: Log Viewer
    with tab6:
        display_log_viewer()
    
    # 탭 7: Alert Rules
    with tab7:
        display_alert_rules()


if __name__ == "__main__":
    main()
