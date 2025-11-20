#!/usr/bin/env python3
"""
트렌드 분석 실행 스크립트
명령줄에서 직접 분석 실행
"""

import argparse
import json
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.services.trend_service import TrendService

logger = setup_logger("analysis", level=logging.INFO)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="뉴스 트렌드 분석 실행",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python scripts/run_analysis.py --keyword "AI"
  python scripts/run_analysis.py --keyword "AI" --max-results 200 --output results.json
        """,
    )
    
    parser.add_argument(
        "--keyword",
        type=str,
        required=True,
        help="분석할 키워드",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="최대 수집 뉴스 개수 (기본값: 100)",
    )
    parser.add_argument(
        "--time-window",
        type=int,
        default=24,
        help="시간 윈도우 (시간) (기본값: 24)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="결과 저장 파일 경로 (JSON)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config_api.yaml",
        help="설정 파일 경로",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="상세 로그 출력",
    )
    
    args = parser.parse_args()
    
    # 로그 레벨 설정
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 설정 로드
    try:
        config = load_config(args.config)
        logger.info(f"설정 파일 로드 완료: {args.config}")
    except Exception as e:
        logger.warning(f"설정 파일 로드 실패, 기본 설정 사용: {e}")
        config = {}
    
    # 서비스 초기화
    try:
        service = TrendService(config_path=args.config)
        logger.info("트렌드 분석 서비스 초기화 완료")
    except Exception as e:
        logger.error(f"서비스 초기화 실패: {e}")
        sys.exit(1)
    
    # 분석 실행
    logger.info(f"트렌드 분석 시작: {args.keyword}")
    try:
        result = service.analyze_trend(
            keyword=args.keyword,
            max_results=args.max_results,
            time_window_hours=args.time_window,
        )
    except Exception as e:
        logger.error(f"분석 실행 실패: {e}")
        sys.exit(1)
    
    # 결과 출력
    print("\n" + "="*60)
    print(f"키워드: {result['keyword']}")
    print(f"총 뉴스 개수: {result['total_news']}")
    print(f"평균 감정 점수: {result['avg_sentiment']:.3f}")
    print(f"스파이크 개수: {len(result['spikes'])}")
    
    anomalies = result.get("anomalies", {})
    zscore_count = len(anomalies.get("zscore", []))
    moving_avg_count = len(anomalies.get("moving_average", []))
    print(f"이상치 개수 (Z-score): {zscore_count}")
    print(f"이상치 개수 (Moving Avg): {moving_avg_count}")
    print(f"분석 시간: {result['analyzed_at']}")
    print("="*60 + "\n")
    
    # 스파이크 정보 출력
    if result['spikes']:
        print("스파이크 정보:")
        for i, spike in enumerate(result['spikes'][:5], 1):  # 최대 5개만
            print(f"  {i}. 시간: {spike.get('timestamp', 'N/A')}, "
                  f"값: {spike.get('value', 0):.3f}, "
                  f"점수: {spike.get('score', 0):.3f}")
        if len(result['spikes']) > 5:
            print(f"  ... 외 {len(result['spikes']) - 5}개")
        print()
    
    # 파일 저장
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"결과 저장 완료: {args.output}")
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
