"""
텍스트 정제 모듈 테스트
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.text_cleaner import TextCleaner


class TestTextCleaner:
    """텍스트 정제기 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        cleaner = TextCleaner()
        assert cleaner is not None
    
    def test_clean_text_basic(self):
        """기본 텍스트 정제 테스트"""
        cleaner = TextCleaner()
        text = "  Hello   World  "
        cleaned = cleaner.clean_text(text)
        assert cleaned == "Hello World"
    
    def test_clean_text_html_removal(self):
        """HTML 태그 제거 테스트"""
        cleaner = TextCleaner()
        text = "<p>Hello <b>World</b></p>"
        cleaned = cleaner.clean_text(text, remove_html=True)
        assert "<" not in cleaned
        assert ">" not in cleaned
    
    def test_clean_text_url_removal(self):
        """URL 제거 테스트"""
        cleaner = TextCleaner()
        text = "Visit https://example.com for more info"
        cleaned = cleaner.clean_text(text, remove_urls=True)
        assert "https://example.com" not in cleaned
    
    def test_clean_text_emoji_removal(self):
        """이모지 제거 테스트"""
        cleaner = TextCleaner()
        text = "Hello 😀 World 🎉"
        cleaned = cleaner.clean_text(text, remove_emoji=True)
        assert "😀" not in cleaned
        assert "🎉" not in cleaned
    
    def test_clean_text_empty(self):
        """빈 텍스트 테스트"""
        cleaner = TextCleaner()
        assert cleaner.clean_text("") == ""
        assert cleaner.clean_text(None) == ""
    
    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        cleaner = TextCleaner()
        text = "AI technology is advancing rapidly. AI and machine learning are important."
        keywords = cleaner.extract_keywords(text, top_k=3)
        
        assert len(keywords) <= 3
        assert "AI" in keywords or "ai" in keywords.lower()
    
    def test_extract_keywords_empty(self):
        """빈 텍스트 키워드 추출 테스트"""
        cleaner = TextCleaner()
        keywords = cleaner.extract_keywords("")
        assert len(keywords) == 0
    
    def test_is_korean_dominant(self):
        """한국어 우세 판단 테스트"""
        cleaner = TextCleaner()
        
        korean_text = "안녕하세요 반갑습니다"
        assert cleaner.is_korean_dominant(korean_text) is True
        
        english_text = "Hello World"
        assert cleaner.is_korean_dominant(english_text) is False
    
    def test_clean_batch(self):
        """배치 정제 테스트"""
        cleaner = TextCleaner()
        texts = ["  Text 1  ", "  Text 2  ", "  Text 3  "]
        cleaned = cleaner.clean_batch(texts)
        
        assert len(cleaned) == 3
        assert all("  " not in text for text in cleaned)

