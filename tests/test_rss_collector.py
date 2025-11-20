"""
RSS 수집기 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.rss_collector import RSSCollector


class TestRSSCollector:
    """RSS 수집기 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        collector = RSSCollector(rss_urls=["https://example.com/rss"])
        assert len(collector.rss_urls) == 1
        assert collector.retry_count == 3
    
    @patch('src.data.rss_collector.feedparser')
    def test_collect_success(self, mock_feedparser):
        """수집 성공 테스트"""
        # Mock feedparser 반환값 설정
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry1 = MagicMock()
        mock_entry1.get.side_effect = lambda key, default="": {
            "title": "Test News 1",
            "link": "https://example.com/1",
            "summary": "Test summary 1",
            "published": "2024-01-15 10:00:00"
        }.get(key, default)
        mock_entry1.tags = []
        
        mock_entry2 = MagicMock()
        mock_entry2.get.side_effect = lambda key, default="": {
            "title": "Test News 2",
            "link": "https://example.com/2",
            "summary": "Test summary 2",
            "published": "2024-01-15 11:00:00"
        }.get(key, default)
        mock_entry2.tags = []
        
        mock_feed.entries = [mock_entry1, mock_entry2]
        mock_feed.feed.get.return_value = "Test Feed"
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(rss_urls=["https://example.com/rss"])
        results = collector.collect(keyword="Test", max_results=10)
        
        assert len(results) > 0
        assert all("title" in item for item in results)
        assert all("link" in item for item in results)
    
    @patch('src.data.rss_collector.feedparser')
    def test_collect_with_keyword_filter(self, mock_feedparser):
        """키워드 필터링 테스트"""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda key, default="": {
            "title": "AI Technology News",
            "link": "https://example.com/1",
            "summary": "AI related content",
            "published": "2024-01-15 10:00:00"
        }.get(key, default)
        mock_entry.tags = []
        mock_feed.entries = [mock_entry]
        mock_feed.feed.get.return_value = "Test Feed"
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(rss_urls=["https://example.com/rss"])
        results = collector.collect(keyword="AI", max_results=10)
        
        assert len(results) > 0
    
    @patch('src.data.rss_collector.feedparser')
    def test_collect_empty_feed(self, mock_feedparser):
        """빈 피드 테스트"""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = []
        mock_feed.feed.get.return_value = "Test Feed"
        mock_feedparser.parse.return_value = mock_feed
        
        collector = RSSCollector(rss_urls=["https://example.com/rss"])
        results = collector.collect(max_results=10)
        
        assert len(results) == 0
    
    def test_deduplicate_by_link(self):
        """중복 제거 테스트"""
        collector = RSSCollector()
        items = [
            {"link": "https://example.com/1", "title": "News 1"},
            {"link": "https://example.com/1", "title": "News 1 Duplicate"},
            {"link": "https://example.com/2", "title": "News 2"},
        ]
        
        unique = collector._deduplicate_by_link(items)
        assert len(unique) == 2
        assert unique[0]["link"] == "https://example.com/1"
        assert unique[1]["link"] == "https://example.com/2"

