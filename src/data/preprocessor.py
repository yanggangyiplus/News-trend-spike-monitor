"""
텍스트 전처리 모듈
뉴스 텍스트 정제, 정규화, 중복 제거 등
"""

import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """텍스트 전처리 클래스"""
    
    def __init__(self):
        """전처리기 초기화"""
        logger.info("텍스트 전처리기 초기화 완료")
    
    def clean_text(self, text: str) -> str:
        """
        텍스트 정제
        
        Args:
            text: 원본 텍스트
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r"<[^>]+>", "", text)
        
        # URL 제거
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)
        
        # 특수 문자 정리
        text = re.sub(r"[^\w\s가-힣]", " ", text)
        
        # 연속된 공백 제거
        text = re.sub(r"\s+", " ", text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def preprocess_news(self, news_items: List[Dict]) -> List[Dict]:
        """
        뉴스 아이템 리스트 전처리
        
        Args:
            news_items: 원본 뉴스 아이템 리스트
            
        Returns:
            전처리된 뉴스 아이템 리스트
        """
        processed_items = []
        
        for item in news_items:
            processed_item = item.copy()
            
            # 제목 정제
            if "title" in processed_item:
                processed_item["title"] = self.clean_text(processed_item["title"])
            
            # 요약 정제
            if "summary" in processed_item:
                processed_item["summary"] = self.clean_text(processed_item["summary"])
            
            # 빈 텍스트 필터링
            if processed_item.get("title") or processed_item.get("summary"):
                processed_items.append(processed_item)
        
        logger.info(f"전처리 완료: {len(processed_items)}/{len(news_items)}개 아이템")
        return processed_items
    
    def deduplicate(self, news_items: List[Dict], key: str = "link") -> List[Dict]:
        """
        중복 제거
        
        Args:
            news_items: 뉴스 아이템 리스트
            key: 중복 판단 기준 필드
            
        Returns:
            중복 제거된 리스트
        """
        seen = set()
        unique_items = []
        
        for item in news_items:
            value = item.get(key, "")
            if value and value not in seen:
                seen.add(value)
                unique_items.append(item)
        
        logger.info(f"중복 제거 완료: {len(unique_items)}/{len(news_items)}개 아이템")
        return unique_items

