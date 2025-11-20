"""
뉴스 데이터 수집 모듈
RSS, Google News API 등을 통한 뉴스 데이터 수집
"""

import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """데이터 수집기 기본 클래스"""
    
    @abstractmethod
    def collect(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        키워드 기반 데이터 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            수집된 데이터 리스트
        """
        pass


class RSSCollector(BaseCollector):
    """RSS 피드 기반 뉴스 수집기"""
    
    def __init__(self, rss_urls: Optional[List[str]] = None):
        """
        RSS 수집기 초기화
        
        Args:
            rss_urls: RSS 피드 URL 리스트
        """
        self.rss_urls = rss_urls or []
        logger.info(f"RSS 수집기 초기화 완료: {len(self.rss_urls)}개 피드")
    
    def collect(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        RSS 피드에서 키워드 관련 뉴스 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            뉴스 데이터 리스트
        """
        results = []
        
        for rss_url in self.rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:max_results]:
                    # 키워드 필터링
                    if keyword.lower() in entry.get("title", "").lower() or \
                       keyword.lower() in entry.get("summary", "").lower():
                        
                        news_item = {
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", ""),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                            "source": rss_url,
                            "keyword": keyword,
                            "collected_at": datetime.now().isoformat(),
                        }
                        results.append(news_item)
                
                logger.info(f"RSS 피드에서 {len(results)}개 뉴스 수집: {rss_url}")
            
            except Exception as e:
                logger.error(f"RSS 피드 수집 오류 ({rss_url}): {e}")
        
        return results[:max_results]


class GoogleNewsCollector(BaseCollector):
    """Google News API 기반 뉴스 수집기"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Google News 수집기 초기화
        
        Args:
            api_key: Google News API 키 (선택사항)
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
        logger.info("Google News 수집기 초기화 완료")
    
    def collect(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        Google News API에서 키워드 관련 뉴스 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            뉴스 데이터 리스트
        """
        if not self.api_key:
            logger.warning("Google News API 키가 설정되지 않았습니다. Mock 데이터를 반환합니다.")
            return self._get_mock_data(keyword, max_results)
        
        results = []
        
        try:
            params = {
                "q": keyword,
                "apiKey": self.api_key,
                "pageSize": min(max_results, 100),
                "language": "ko",
                "sortBy": "publishedAt",
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get("articles", []):
                news_item = {
                    "title": article.get("title", ""),
                    "summary": article.get("description", ""),
                    "link": article.get("url", ""),
                    "published": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "keyword": keyword,
                    "collected_at": datetime.now().isoformat(),
                }
                results.append(news_item)
            
            logger.info(f"Google News에서 {len(results)}개 뉴스 수집: {keyword}")
        
        except Exception as e:
            logger.error(f"Google News API 수집 오류: {e}")
            return self._get_mock_data(keyword, max_results)
        
        return results
    
    def _get_mock_data(self, keyword: str, max_results: int) -> List[Dict]:
        """Mock 데이터 생성 (API 키 없을 때)"""
        return [
            {
                "title": f"{keyword} 관련 뉴스 {i+1}",
                "summary": f"{keyword}에 대한 뉴스 요약 내용입니다.",
                "link": f"https://example.com/news/{i+1}",
                "published": datetime.now().isoformat(),
                "source": "Mock Source",
                "keyword": keyword,
                "collected_at": datetime.now().isoformat(),
            }
            for i in range(min(max_results, 10))
        ]


class NewsCollector:
    """통합 뉴스 수집기"""
    
    def __init__(
        self,
        rss_urls: Optional[List[str]] = None,
        google_news_api_key: Optional[str] = None,
    ):
        """
        통합 뉴스 수집기 초기화
        
        Args:
            rss_urls: RSS 피드 URL 리스트
            google_news_api_key: Google News API 키
        """
        self.rss_collector = RSSCollector(rss_urls)
        self.google_collector = GoogleNewsCollector(google_news_api_key)
        logger.info("통합 뉴스 수집기 초기화 완료")
    
    def collect(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """
        모든 소스에서 뉴스 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            통합 뉴스 데이터 리스트
        """
        all_results = []
        
        # RSS 수집
        rss_results = self.rss_collector.collect(keyword, max_results)
        all_results.extend(rss_results)
        
        # Google News 수집
        google_results = self.google_collector.collect(keyword, max_results)
        all_results.extend(google_results)
        
        # 중복 제거 (링크 기준)
        seen_links = set()
        unique_results = []
        for item in all_results:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                unique_results.append(item)
        
        logger.info(f"총 {len(unique_results)}개 고유 뉴스 수집 완료: {keyword}")
        return unique_results[:max_results]

