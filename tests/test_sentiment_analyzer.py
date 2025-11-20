"""
감정 분석기 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.nlp.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """감정 분석기 테스트 클래스"""
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_init(self, mock_pipeline):
        """초기화 테스트"""
        mock_pipeline.return_value = MagicMock()
        analyzer = SentimentAnalyzer()
        assert analyzer is not None
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_analyze_single_text(self, mock_pipeline):
        """단일 텍스트 분석 테스트"""
        # Mock pipeline 설정
        mock_analyzer = MagicMock()
        mock_analyzer.return_value = [
            [
                {"label": "POSITIVE", "score": 0.9},
                {"label": "NEGATIVE", "score": 0.1}
            ]
        ]
        mock_pipeline.return_value = mock_analyzer
        
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("This is a positive text")
        
        assert "positive" in result
        assert "negative" in result
        assert "confidence" in result
        assert 0.0 <= result["positive"] <= 1.0
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_analyze_empty_text(self, mock_pipeline):
        """빈 텍스트 분석 테스트"""
        mock_pipeline.return_value = MagicMock()
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("")
        
        assert result["positive"] == 0.5
        assert result["negative"] == 0.5
        assert result["confidence"] == 0.0
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_analyze_batch(self, mock_pipeline):
        """배치 분석 테스트"""
        mock_analyzer = MagicMock()
        mock_analyzer.return_value = [
            [{"label": "POSITIVE", "score": 0.8}],
            [{"label": "NEGATIVE", "score": 0.7}]
        ]
        mock_pipeline.return_value = mock_analyzer
        
        analyzer = SentimentAnalyzer()
        results = analyzer.analyze(["Text 1", "Text 2"])
        
        assert len(results) == 2
        assert all("positive" in r for r in results)
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_get_sentiment_score(self, mock_pipeline):
        """감정 점수 반환 테스트"""
        mock_analyzer = MagicMock()
        mock_analyzer.return_value = [
            [{"label": "POSITIVE", "score": 0.8}]
        ]
        mock_pipeline.return_value = mock_analyzer
        
        analyzer = SentimentAnalyzer()
        score = analyzer.get_sentiment_score("Positive text")
        
        assert 0.0 <= score <= 1.0
    
    @patch('src.nlp.sentiment_analyzer.pipeline')
    def test_get_confidence(self, mock_pipeline):
        """신뢰도 반환 테스트"""
        mock_analyzer = MagicMock()
        mock_analyzer.return_value = [
            [{"label": "POSITIVE", "score": 0.9}]
        ]
        mock_pipeline.return_value = mock_analyzer
        
        analyzer = SentimentAnalyzer()
        confidence = analyzer.get_confidence("Text")
        
        assert 0.0 <= confidence <= 1.0

