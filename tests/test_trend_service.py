"""
트렌드 분석 서비스 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.trend_service import TrendService


class TestTrendService:
    """트렌드 분석 서비스 테스트 클래스"""
    
    @patch('src.services.trend_service.RSSCollector')
    @patch('src.services.trend_service.GoogleNewsCollector')
    @patch('src.services.trend_service.SentimentAnalyzer')
    def test_init(self, mock_sentiment, mock_google, mock_rss):
        """초기화 테스트"""
        service = TrendService()
        assert service is not None
    
    @patch('src.services.trend_service.RSSCollector')
    @patch('src.services.trend_service.GoogleNewsCollector')
    @patch('src.services.trend_service.SentimentAnalyzer')
    def test_analyze_trend_empty_keyword(self, mock_sentiment, mock_google, mock_rss):
        """빈 키워드 분석 테스트"""
        # Mock 설정
        mock_rss_instance = MagicMock()
        mock_rss_instance.collect.return_value = []
        mock_rss.return_value = mock_rss_instance
        
        mock_google_instance = MagicMock()
        mock_google_instance.collect.return_value = []
        mock_google.return_value = mock_google_instance
        
        service = TrendService()
        result = service.analyze_trend(keyword="", max_results=10)
        
        assert result["total_news"] == 0
        assert result["keyword"] == ""
    
    @patch('src.services.trend_service.RSSCollector')
    @patch('src.services.trend_service.GoogleNewsCollector')
    @patch('src.services.trend_service.SentimentAnalyzer')
    def test_analyze_trend_with_data(self, mock_sentiment, mock_google, mock_rss):
        """데이터 포함 분석 테스트"""
        # Mock 뉴스 데이터
        mock_news = [
            {
                "title": "Test News",
                "link": "https://example.com/1",
                "pubDate": "2024-01-15 10:00:00",
                "summary": "Test summary",
                "source": "Test Source"
            }
        ]
        
        # Mock 설정
        mock_rss_instance = MagicMock()
        mock_rss_instance.collect.return_value = mock_news
        mock_rss.return_value = mock_rss_instance
        
        mock_google_instance = MagicMock()
        mock_google_instance.collect.return_value = []
        mock_google.return_value = mock_google_instance
        
        mock_sentiment_instance = MagicMock()
        mock_sentiment_instance.analyze.return_value = {
            "positive": 0.7,
            "negative": 0.3,
            "neutral": 0.0,
            "confidence": 0.8
        }
        mock_sentiment.return_value = mock_sentiment_instance
        
        service = TrendService()
        result = service.analyze_trend(keyword="Test", max_results=10)
        
        assert result["keyword"] == "Test"
        assert "time_series" in result
        assert "spikes" in result
        assert "anomalies" in result
    
    def test_empty_result(self):
        """빈 결과 반환 테스트"""
        service = TrendService()
        result = service._empty_result("Test")
        
        assert result["keyword"] == "Test"
        assert result["total_news"] == 0
        assert result["avg_sentiment"] == 0.5
        assert len(result["time_series"]) == 0

