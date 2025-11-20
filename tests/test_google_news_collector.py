"""
Google News 수집기 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.google_news_collector import GoogleNewsCollector


class TestGoogleNewsCollector:
    """Google News 수집기 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        collector = GoogleNewsCollector(api_key="test_key")
        assert collector.api_key == "test_key"
        assert collector.base_url == "https://newsapi.org/v2/everything"
    
    def test_init_without_api_key(self):
        """API 키 없이 초기화 테스트"""
        collector = GoogleNewsCollector()
        assert collector.api_key is None
    
    @patch('src.data.google_news_collector.requests.get')
    def test_collect_success(self, mock_get):
        """수집 성공 테스트"""
        # Mock API 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test News 1",
                    "url": "https://example.com/1",
                    "description": "Test description 1",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "source": {"name": "Test Source"},
                    "urlToImage": ""
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        collector = GoogleNewsCollector(api_key="test_key")
        results = collector.collect(keyword="Test", max_results=10)
        
        assert len(results) > 0
        assert all("title" in item for item in results)
        assert all("link" in item for item in results)
    
    @patch('src.data.google_news_collector.requests.get')
    def test_collect_api_error(self, mock_get):
        """API 오류 테스트"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        collector = GoogleNewsCollector(api_key="test_key")
        
        with pytest.raises(Exception):
            collector.collect(keyword="Test", max_results=10)
    
    @patch('src.data.google_news_collector.requests.get')
    def test_collect_timeout(self, mock_get):
        """타임아웃 테스트"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        collector = GoogleNewsCollector(api_key="test_key")
        
        with pytest.raises(requests.exceptions.Timeout):
            collector.collect(keyword="Test", max_results=10)
    
    def test_collect_without_api_key(self):
        """API 키 없이 수집 테스트"""
        collector = GoogleNewsCollector()
        results = collector.collect(keyword="Test", max_results=10)
        
        assert len(results) == 0
    
    def test_normalize_pubdate(self):
        """날짜 정규화 테스트"""
        collector = GoogleNewsCollector()
        
        # ISO 8601 형식
        normalized = collector._normalize_pubdate("2024-01-15T10:00:00Z")
        assert normalized == "2024-01-15 10:00:00"
        
        # 빈 문자열
        normalized = collector._normalize_pubdate("")
        assert "2024" in normalized  # 현재 날짜 포함

