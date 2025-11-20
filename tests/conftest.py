"""
pytest 설정 파일
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_news_data():
    """샘플 뉴스 데이터 fixture"""
    return [
        {
            "title": "Test News 1",
            "link": "https://example.com/1",
            "pubDate": "2024-01-15 10:00:00",
            "summary": "Test summary 1",
            "source": "Test Source"
        },
        {
            "title": "Test News 2",
            "link": "https://example.com/2",
            "pubDate": "2024-01-15 11:00:00",
            "summary": "Test summary 2",
            "source": "Test Source"
        }
    ]


@pytest.fixture
def sample_time_series_data():
    """샘플 시계열 데이터 fixture"""
    return [
        {"timestamp": "2024-01-15T10:00:00", "avg_sentiment": 0.5, "count": 5},
        {"timestamp": "2024-01-15T11:00:00", "avg_sentiment": 0.7, "count": 3},
        {"timestamp": "2024-01-15T12:00:00", "avg_sentiment": 0.3, "count": 8},
    ]

