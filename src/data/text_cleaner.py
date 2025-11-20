"""
텍스트 전처리 모듈
뉴스 텍스트 정제 및 키워드 추출
"""

import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """텍스트 정제 클래스"""
    
    # 이모지 패턴 (유니코드 범위)
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "]+",
        flags=re.UNICODE
    )
    
    # URL 패턴
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    # 반복 문자 패턴 (예: "와아아아" -> "와아")
    REPEAT_PATTERN = re.compile(r'(.)\1{2,}')
    
    # 한국어 stopwords (기본)
    KOREAN_STOPWORDS = {
        "이", "가", "을", "를", "에", "의", "와", "과", "도", "로", "으로",
        "은", "는", "이다", "있다", "없다", "하다", "되다", "그", "그것",
        "이것", "저것", "그런", "이런", "저런", "그렇게", "이렇게", "저렇게",
    }
    
    def clean_text(
        self,
        text: str,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_emoji: bool = True,
        normalize_whitespace: bool = True,
        remove_stopwords: bool = False,
    ) -> str:
        """
        뉴스 텍스트 전처리
        
        Args:
            text: 원본 텍스트
            remove_html: HTML 태그 제거 여부
            remove_urls: URL 제거 여부
            remove_emoji: 이모지 제거 여부
            normalize_whitespace: 공백 정규화 여부
            remove_stopwords: stopwords 제거 여부
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return ""
        
        # 1. HTML 태그 제거
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
        
        # 2. URL 제거
        if remove_urls:
            text = self.URL_PATTERN.sub('', text)
        
        # 3. 이메일 제거
        text = re.sub(r'\S+@\S+', '', text)
        
        # 4. 이모지 제거
        if remove_emoji:
            text = self.EMOJI_PATTERN.sub('', text)
        
        # 5. 반복 문자 축약 (예: "와아아아" -> "와아")
        text = self.REPEAT_PATTERN.sub(r'\1\1', text)
        
        # 6. 특수 문자 정리 (한글, 영문, 숫자, 기본 구두점, 공백만 유지)
        # 한글 자음/모음도 유지 (ㅋ, ㅎ 등 웃음 표현 보존)
        text = re.sub(r'[^\w\s가-힣\u3131-\u3163.,!?]', ' ', text)
        
        # 7. Stopwords 제거
        if remove_stopwords:
            words = text.split()
            words = [w for w in words if w not in self.KOREAN_STOPWORDS]
            text = ' '.join(words)
        
        # 8. 공백 정규화
        if normalize_whitespace:
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    def extract_keywords(
        self,
        text: str,
        top_k: int = 5,
        min_length: int = 2,
    ) -> List[str]:
        """
        키워드 추출 (빈도 기반)
        
        Args:
            text: 텍스트
            top_k: 추출할 키워드 개수
            min_length: 최소 단어 길이
            
        Returns:
            키워드 리스트
        """
        if not text:
            return []
        
        # 텍스트 정제
        cleaned_text = self.clean_text(
            text,
            remove_html=True,
            remove_urls=True,
            remove_emoji=True,
            normalize_whitespace=True,
            remove_stopwords=True,
        )
        
        # 단어 분리 및 빈도 계산
        words = cleaned_text.split()
        word_freq = {}
        
        for word in words:
            # 최소 길이 필터링
            if len(word) < min_length:
                continue
            
            # Stopwords 제외
            if word in self.KOREAN_STOPWORDS:
                continue
            
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 k개 추출
        keywords = [word for word, _ in sorted_words[:top_k]]
        
        return keywords
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        배치 텍스트 정제
        
        Args:
            texts: 텍스트 리스트
            
        Returns:
            정제된 텍스트 리스트
        """
        return [self.clean_text(text) for text in texts]
    
    def is_korean_dominant(self, text: str, threshold: float = 0.5) -> bool:
        """
        한국어가 주된 언어인지 확인
        
        Args:
            text: 텍스트
            threshold: 한국어 비율 임계값
            
        Returns:
            한국어가 주된 언어인지 여부
        """
        if not text:
            return False
        
        korean_pattern = re.compile(r'[가-힣]')
        total_chars = len(re.findall(r'[가-힣a-zA-Z0-9]', text))
        
        if total_chars == 0:
            return False
        
        korean_chars = len(korean_pattern.findall(text))
        korean_ratio = korean_chars / total_chars
        
        return korean_ratio >= threshold

