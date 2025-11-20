"""
뉴스 상세 목록 컴포넌트
"""

import streamlit as st
import pandas as pd
from typing import Dict
import re
import logging

from app.web.components.theme import get_sentiment_color

logger = logging.getLogger(__name__)


def highlight_keyword(text: str, keyword: str) -> str:
    """
    텍스트에서 키워드 하이라이팅
    
    Args:
        text: 원본 텍스트
        keyword: 하이라이팅할 키워드
        
    Returns:
        하이라이팅된 텍스트 (HTML)
    """
    if not keyword or not text:
        return text
    
    # 대소문자 구분 없이 하이라이팅
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    highlighted = pattern.sub(
        lambda m: f'<mark style="background-color: yellow; font-weight: bold;">{m.group()}</mark>',
        text
    )
    
    return highlighted


def display_news_list(result: Dict):
    """
    키워드별 기사 상세 리스트 표시
    
    Args:
        result: 분석 결과 딕셔너리
    """
    news_items = result.get("news_items", [])
    keyword = result.get("keyword", "")
    
    if not news_items:
        st.info("뉴스 데이터가 없습니다")
        return
    
    # 데이터프레임 생성
    df_data = []
    for item in news_items:
        title = item.get("title", "제목 없음")
        summary = item.get("summary", "요약 없음")
        
        # 키워드 하이라이팅
        if keyword:
            title = highlight_keyword(title, keyword)
            summary = highlight_keyword(summary, keyword)
        
        df_data.append({
            "제목": title,
            "요약": summary[:100] + "..." if len(summary) > 100 else summary,
            "감정 점수": item.get("sentiment_score", 0.5),
            "신뢰도": item.get("confidence", 0.0),
            "출처": item.get("source", "알 수 없음"),
            "발행일": item.get("pubDate", "알 수 없음"),
            "링크": item.get("link", ""),
        })
    
    df = pd.DataFrame(df_data)
    
    # 감정 점수에 따라 색상 분기 및 컬러 인디케이터
    def color_sentiment(val):
        score = float(val)
        bg_color, _ = get_sentiment_color(score)
        return f"background-color: {bg_color}"
    
    def add_color_indicator(row):
        score = row["감정 점수"]
        _, emoji = get_sentiment_color(score)
        return emoji
    
    # 컬러 인디케이터 추가
    df["상태"] = df.apply(add_color_indicator, axis=1)
    
    # 스타일 적용
    styled_df = df.style.applymap(color_sentiment, subset=["감정 점수"])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
    )
    
    # 상세 정보 표시
    st.subheader("기사 상세 정보")
    for i, item in enumerate(news_items[:10], 1):  # 최대 10개만 표시
        title = item.get('title', '제목 없음')
        sentiment_score = item.get('sentiment_score', 0.5)
        
        # 감정 점수에 따른 이모지 추가
        _, emoji = get_sentiment_color(sentiment_score)
        
        with st.expander(f"{emoji} {i}. {title}"):
            st.markdown(f"**요약**: {item.get('summary', '요약 없음')}", unsafe_allow_html=True)
            st.write(f"**링크**: {item.get('link', '')}")
            st.write(f"**출처**: {item.get('source', '알 수 없음')}")
            
            # 감정 점수 컬러 인디케이터
            col1, col2 = st.columns(2)
            with col1:
                st.metric("감정 점수", f"{sentiment_score:.3f}")
            with col2:
                st.metric("신뢰도", f"{item.get('confidence', 0.0):.3f}")
            
            st.write(f"**발행일**: {item.get('pubDate', '알 수 없음')}")

