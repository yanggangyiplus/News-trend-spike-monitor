"""
RSS 피드 수집 모듈
여러 언론사 RSS feed를 주기적으로 수집
"""

import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time
from src.utils.config import load_config

logger = logging.getLogger(__name__)


class RSSCollector:
    """RSS 피드 기반 뉴스 수집기"""
    
    def __init__(self, rss_urls: Optional[List[str]] = None, config_path: Optional[str] = None):
        """
        RSS 수집기 초기화
        
        Args:
            rss_urls: RSS 피드 URL 리스트
            config_path: 설정 파일 경로 (config_collector.yaml)
        """
        if config_path:
            try:
                config = load_config(config_path)
                collector_config = config.get("collector", {})
                self.rss_urls = collector_config.get("rss_urls", [])
                self.retry_count = collector_config.get("retry_count", 3)
                self.retry_delay = collector_config.get("retry_delay", 1)
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
                self.rss_urls = rss_urls or []
                self.retry_count = 3
                self.retry_delay = 1
        else:
            self.rss_urls = rss_urls or []
            self.retry_count = 3
            self.retry_delay = 1
        
        logger.info(f"RSS 수집기 초기화 완료: {len(self.rss_urls)}개 피드")
    
    def collect(self, keyword: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """
        RSS 피드에서 뉴스 수집
        
        Args:
            keyword: 검색 키워드 (None이면 모든 뉴스 수집)
            max_results: 최대 수집 개수
            
        Returns:
            뉴스 데이터 리스트
        """
        all_results = []
        
        for rss_url in self.rss_urls:
            try:
                results = self._collect_from_feed(rss_url, keyword, max_results)
                all_results.extend(results)
                logger.info(f"RSS 피드에서 {len(results)}개 뉴스 수집: {rss_url}")
            
            except Exception as e:
                logger.error(f"RSS 피드 수집 실패 ({rss_url}): {e}")
        
        # 중복 제거 (링크 기준)
        unique_results = self._deduplicate_by_link(all_results)
        
        # 최대 개수 제한
        return unique_results[:max_results]
    
    def _collect_from_feed(
        self,
        rss_url: str,
        keyword: Optional[str],
        max_results: int,
    ) -> List[Dict]:
        """
        단일 RSS 피드에서 수집 (재시도 로직 포함)
        
        Args:
            rss_url: RSS 피드 URL
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            뉴스 데이터 리스트
        """
        for attempt in range(self.retry_count):
            try:
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logger.warning(f"RSS 파싱 경고 ({rss_url}): {feed.bozo_exception}")
                
                results = []
                
                for entry in feed.entries[:max_results]:
                    # 키워드 필터링
                    if keyword:
                        title = entry.get("title", "").lower()
                        summary = entry.get("summary", "").lower()
                        if keyword.lower() not in title and keyword.lower() not in summary:
                            continue
                    
                    # pubDate 정규화
                    pub_date = self._normalize_pubdate(entry.get("published", ""))
                    
                    news_item = {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "pubDate": pub_date,
                        "summary": entry.get("summary", entry.get("description", "")),
                        "media": entry.get("media_content", [{}])[0].get("url", "") if entry.get("media_content") else "",
                        "category": ", ".join([tag.term for tag in entry.get("tags", [])]),
                        "source": feed.feed.get("title", rss_url),
                        "keyword": keyword or "",
                        "collected_at": datetime.now().isoformat(),
                    }
                    results.append(news_item)
                
                return results
            
            except Exception as e:
                if attempt < self.retry_count - 1:
                    logger.warning(f"RSS 수집 재시도 ({attempt + 1}/{self.retry_count}): {rss_url}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"RSS 피드 수집 실패 (최대 재시도 초과): {rss_url}")
                    raise
        
        return []
    
    def _normalize_pubdate(self, pub_date_str: str) -> str:
        """
        pubDate를 Y-m-d H:M:S 형식으로 정규화
        
        Args:
            pub_date_str: 원본 날짜 문자열
            
        Returns:
            정규화된 날짜 문자열 (Y-m-d H:M:S)
        """
        if not pub_date_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # feedparser가 파싱한 시간 사용
            from feedparser import _parse_date
            parsed_time = _parse_date(pub_date_str)
            if parsed_time:
                return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        
        # 파싱 실패 시 현재 시간 반환
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _deduplicate_by_link(self, news_items: List[Dict]) -> List[Dict]:
        """
        링크 기준 중복 제거
        
        Args:
            news_items: 뉴스 아이템 리스트
            
        Returns:
            중복 제거된 리스트
        """
        seen_links = set()
        unique_items = []
        
        for item in news_items:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                unique_items.append(item)
        
        return unique_items

