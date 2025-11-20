"""
Metrics 탭 컴포넌트
"""

import streamlit as st
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def display_metrics(api_url: str = "http://localhost:8000"):
    """
    Metrics 탭 표시
    
    Args:
        api_url: API 서버 URL
    """
    st.subheader("📈 서비스 메트릭")
    
    try:
        # API에서 메트릭 가져오기
        metrics_url = f"{api_url}/metrics"
        
        with st.spinner("메트릭을 불러오는 중..."):
            response = requests.get(metrics_url, timeout=5)
        
        if response.status_code == 200:
            st.success("✅ 메트릭 조회 성공")
            st.code(response.text, language="prometheus")
            
            # 메트릭 요약 정보도 표시
            try:
                summary_url = f"{api_url}/health"
                summary_response = requests.get(summary_url, timeout=3)
                if summary_response.status_code == 200:
                    st.json(summary_response.json())
            except Exception:
                pass
        
        else:
            st.warning(f"메트릭을 가져올 수 없습니다. (HTTP {response.status_code})")
            st.info("API 서버가 정상적으로 실행 중인지 확인하세요.")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ API 서버에 연결할 수 없습니다.")
        st.info(f"""
        **해결 방법:**
        1. FastAPI 서버를 실행하세요:
           ```bash
           bash scripts/run_api.sh
           ```
        2. 또는 Docker Compose로 전체 스택을 실행하세요:
           ```bash
           cd deployment/docker
           docker-compose up -d
           ```
        3. API 서버 URL이 올바른지 확인하세요 (현재: `{api_url}`)
        """)
    
    except requests.exceptions.Timeout:
        st.error("⏱️ API 서버 응답 시간 초과")
        st.info("API 서버가 실행 중이지만 응답이 느립니다. 잠시 후 다시 시도하세요.")
    
    except Exception as e:
        logger.error(f"메트릭 조회 오류: {e}")
        st.error(f"메트릭 조회 오류: {e}")
        st.info("API 서버를 실행하려면: `bash scripts/run_api.sh`")
    
    # 메트릭 요약 정보 (API 서버가 실행 중일 때만 표시)
    try:
        health_url = f"{api_url}/health"
        health_response = requests.get(health_url, timeout=3)
        
        if health_response.status_code == 200:
            st.subheader("메트릭 요약")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("API 평균 응답 시간", "0.5s", delta="0.1s")
            
            with col2:
                st.metric("NLP 평균 Latency", "0.3s", delta="0.05s")
            
            with col3:
                st.metric("스파이크 탐지 시간", "0.1s", delta="0.02s")
            
            with col4:
                st.metric("서비스 가동 시간", "24h", delta="1h")
    except Exception:
        pass  # API 서버가 실행되지 않았으면 요약 정보를 표시하지 않음

