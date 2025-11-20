"""
Google News API 수집 모듈
Google News API로 키워드 기반 기사 수집
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time
from src.utils.config import load_config

logger = logging.getLogger(__name__)


class GoogleNewsCollector:
    """Google News API 기반 뉴스 수집기"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        """
        Google News 수집기 초기화
        
        Args:
            api_key: Google News API 키 (NewsAPI.org)
            config_path: 설정 파일 경로
        """
        if config_path:
            try:
                config = load_config(config_path)
                collector_config = config.get("collector", {})
                google_news_config = collector_config.get("google_news", {})
                self.api_key = google_news_config.get("api_key") or api_key
                self.base_url = google_news_config.get("base_url", "https://newsapi.org/v2/everything")
                self.language = google_news_config.get("language", "ko")
                self.sort_by = google_news_config.get("sort_by", "publishedAt")
                self.timeout = collector_config.get("timeout", 10)
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
                self.api_key = api_key
                self.base_url = "https://newsapi.org/v2/everything"
                self.language = "ko"
                self.sort_by = "publishedAt"
                self.timeout = 10
        else:
            self.api_key = api_key
            self.base_url = "https://newsapi.org/v2/everything"
            self.language = "ko"
            self.sort_by = "publishedAt"
            self.timeout = 10
        
        logger.info("Google News 수집기 초기화 완료")
    
    def collect(
        self,
        keyword: str,
        max_results: int = 100,
    ) -> List[Dict]:
        """
        Google News API에서 키워드 관련 뉴스 수집
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 수집 개수
            
        Returns:
            뉴스 데이터 리스트
        """
        if not self.api_key:
            logger.warning("Google News API 키가 설정되지 않았습니다. 빈 리스트 반환")
            return []
        
        all_results = []
        page = 1
        page_size = min(100, max_results)  # API 최대 페이지 크기
        
        while len(all_results) < max_results:
            try:
                results = self._fetch_page(keyword, page, page_size)
                
                if not results:
                    break
                
                all_results.extend(results)
                
                # 다음 페이지로
                if len(results) < page_size:
                    break
                
                page += 1
                
                # API rate limit 방지
                time.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Google News API 수집 오류: {e}")
                break
        
        # 최대 개수 제한
        return all_results[:max_results]
    
    def _fetch_page(
        self,
        keyword: str,
        page: int,
        page_size: int,
    ) -> List[Dict]:
        """
        단일 페이지 데이터 가져오기
        
        Args:
            keyword: 검색 키워드
            page: 페이지 번호
            page_size: 페이지 크기
            
        Returns:
            뉴스 데이터 리스트
        """
        params = {
            "q": keyword,
            "apiKey": self.api_key,
            "pageSize": page_size,
            "page": page,
            "language": self.language,
            "sortBy": self.sort_by,
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )
            
            # 응답 상태 확인
            if response.status_code == 429:
                logger.error("Google News API 쿼터 초과. 잠시 후 다시 시도하세요.")
                raise Exception("API 쿼터 초과")
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                error_message = data.get("message", "알 수 없는 오류")
                logger.error(f"Google News API 오류: {error_message}")
                raise Exception(f"API 오류: {error_message}")
            
            articles = data.get("articles", [])
            results = []
            
            for article in articles:
                # pubDate 정규화
                pub_date = self._normalize_pubdate(article.get("publishedAt", ""))
                
                news_item = {
                    "title": article.get("title", ""),
                    "link": article.get("url", ""),
                    "pubDate": pub_date,
                    "summary": article.get("description", ""),
                    "media": article.get("urlToImage", ""),
                    "category": "",
                    "source": article.get("source", {}).get("name", ""),
                    "keyword": keyword,
                    "collected_at": datetime.now().isoformat(),
                }
                results.append(news_item)
            
            return results
        
        except requests.exceptions.Timeout:
            logger.error(f"Google News API 타임아웃 (키워드: {keyword})")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Google News API 요청 오류: {e}")
            raise
    
    def _normalize_pubdate(self, pub_date_str: str) -> str:
        """
        pubDate를 Y-m-d H:M:S 형식으로 정규화
        
        Args:
            pub_date_str: 원본 날짜 문자열 (ISO 8601 형식)
            
        Returns:
            정규화된 날짜 문자열 (Y-m-d H:M:S)
        """
        if not pub_date_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # ISO 8601 형식 파싱
            dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"날짜 파싱 실패 ({pub_date_str}): {e}")
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

