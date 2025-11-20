"""
기본 사용 예제
트렌드 분석 서비스 사용법 예시
"""

from src.services.trend_service import TrendService
from src.utils.logger import setup_logger
import logging

logger = setup_logger("example", level=logging.INFO)


def main():
    """기본 사용 예제"""
    
    # 서비스 초기화
    service = TrendService()
    
    # 키워드 분석
    keyword = "AI"
    result = service.analyze_trend(
        keyword=keyword,
        max_results=50,
        time_window_hours=24,
    )
    
    # 결과 출력
    print(f"\n키워드: {result['keyword']}")
    print(f"총 뉴스 개수: {result['total_news']}")
    print(f"평균 감정 점수: {result['avg_sentiment']:.2f}")
    print(f"스파이크 개수: {len(result['spikes'])}")
    print(f"이상치 개수: {len(result['anomalies'])}")
    
    # 스파이크 정보 출력
    if result['spikes']:
        print("\n스파이크 정보:")
        for spike in result['spikes'][:5]:  # 최대 5개만
            print(f"  - {spike['timestamp']}: {spike['value']:.2f} (Z-score: {spike['z_score']:.2f})")


if __name__ == "__main__":
    main()

