#!/usr/bin/env python3
"""
실시간 뉴스 수집 스케줄러
RSS/Google News를 주기적으로 수집하여 데이터 업데이트
"""

import argparse
import asyncio
import json
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import multiprocessing as mp

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import load_config
from src.utils.logging import setup_logger, log_execution_time
import logging
from src.data.rss_collector import RSSCollector
from src.data.google_news_collector import GoogleNewsCollector
from src.data.text_cleaner import TextCleaner

logger = setup_logger("scheduler", level=logging.INFO)


class NewsScheduler:
    """뉴스 수집 스케줄러 클래스"""
    
    def __init__(
        self,
        keywords: List[str],
        interval_seconds: int = 60,
        output_file: str = "data/processed/news.jsonl",
        config_path: Optional[str] = None,
        use_async: bool = True,
    ):
        """
        스케줄러 초기화
        
        Args:
            keywords: 수집할 키워드 리스트
            interval_seconds: 수집 간격 (초)
            output_file: 출력 파일 경로 (JSONL 형식)
            config_path: 설정 파일 경로
            use_async: 비동기 모드 사용 여부
        """
        self.keywords = keywords
        self.interval_seconds = interval_seconds
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.use_async = use_async
        self.running = True
        
        # 설정 로드
        if config_path:
            try:
                config = load_config(config_path)
                collector_config = config.get("collector", {})
                rss_urls = collector_config.get("rss_urls", [])
                google_news_config = collector_config.get("google_news", {})
                api_key = google_news_config.get("api_key")
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
                rss_urls = []
                api_key = None
        else:
            rss_urls = []
            api_key = None
        
        # 수집기 초기화
        self.rss_collector = RSSCollector(rss_urls=rss_urls, config_path=config_path)
        self.google_collector = GoogleNewsCollector(api_key=api_key, config_path=config_path)
        self.text_cleaner = TextCleaner()
        
        logger.info(f"스케줄러 초기화 완료: {len(keywords)}개 키워드, {interval_seconds}초 간격")
    
    def collect_news(self, keyword: str) -> List[Dict]:
        """
        단일 키워드 뉴스 수집
        
        Args:
            keyword: 수집할 키워드
            
        Returns:
            수집된 뉴스 리스트
        """
        all_news = []
        
        try:
            # RSS 수집
            rss_news = self.rss_collector.collect(keyword=keyword, max_results=50)
            all_news.extend(rss_news)
            logger.info(f"RSS에서 {len(rss_news)}개 뉴스 수집: {keyword}")
        except Exception as e:
            logger.error(f"RSS 수집 오류 ({keyword}): {e}")
        
        try:
            # Google News 수집
            google_news = self.google_collector.collect(keyword=keyword, max_results=50)
            all_news.extend(google_news)
            logger.info(f"Google News에서 {len(google_news)}개 뉴스 수집: {keyword}")
        except Exception as e:
            logger.error(f"Google News 수집 오류 ({keyword}): {e}")
        
        # 중복 제거 및 전처리
        seen_links = set()
        unique_news = []
        
        for item in all_news:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                # 텍스트 정제
                item["title_cleaned"] = self.text_cleaner.clean_text(item.get("title", ""))
                item["summary_cleaned"] = self.text_cleaner.clean_text(item.get("summary", ""))
                item["collected_at"] = datetime.now().isoformat()
                unique_news.append(item)
        
        return unique_news
    
    async def collect_news_async(self, keyword: str) -> List[Dict]:
        """
        비동기 뉴스 수집
        
        Args:
            keyword: 수집할 키워드
            
        Returns:
            수집된 뉴스 리스트
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.collect_news, keyword)
    
    def save_news(self, news_items: List[Dict]):
        """
        뉴스를 JSONL 파일에 저장
        
        Args:
            news_items: 저장할 뉴스 리스트
        """
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                for item in news_items:
                    json.dump(item, f, ensure_ascii=False)
                    f.write("\n")
            logger.info(f"{len(news_items)}개 뉴스 저장 완료: {self.output_file}")
        except Exception as e:
            logger.error(f"뉴스 저장 오류: {e}")
    
    @log_execution_time(logger)
    def run_sync(self):
        """동기 모드 실행"""
        logger.info("동기 모드로 스케줄러 시작")
        
        while self.running:
            try:
                for keyword in self.keywords:
                    news_items = self.collect_news(keyword)
                    if news_items:
                        self.save_news(news_items)
                    
                    # 키워드 간 짧은 대기
                    time.sleep(1)
                
                # 다음 수집까지 대기
                logger.info(f"다음 수집까지 {self.interval_seconds}초 대기...")
                time.sleep(self.interval_seconds)
            
            except KeyboardInterrupt:
                logger.info("스케줄러 종료 요청")
                self.running = False
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 오류: {e}")
                time.sleep(5)  # 오류 후 짧은 대기
    
    async def run_async(self):
        """비동기 모드 실행"""
        logger.info("비동기 모드로 스케줄러 시작")
        
        while self.running:
            try:
                tasks = [self.collect_news_async(keyword) for keyword in self.keywords]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for keyword, result in zip(self.keywords, results):
                    if isinstance(result, Exception):
                        logger.error(f"수집 오류 ({keyword}): {result}")
                    elif result:
                        self.save_news(result)
                
                # 다음 수집까지 대기
                logger.info(f"다음 수집까지 {self.interval_seconds}초 대기...")
                await asyncio.sleep(self.interval_seconds)
            
            except KeyboardInterrupt:
                logger.info("스케줄러 종료 요청")
                self.running = False
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 오류: {e}")
                await asyncio.sleep(5)
    
    def run(self):
        """스케줄러 실행"""
        if self.use_async:
            asyncio.run(self.run_async())
        else:
            self.run_sync()
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        logger.info("스케줄러 중지됨")


def run_multiprocess(
    keywords: List[str],
    interval_seconds: int,
    output_file: str,
    config_path: Optional[str],
    num_processes: int = 2,
):
    """
    멀티프로세싱 모드 실행
    
    Args:
        keywords: 수집할 키워드 리스트
        interval_seconds: 수집 간격
        output_file: 출력 파일 경로
        config_path: 설정 파일 경로
        num_processes: 프로세스 개수
    """
    def worker(keyword: str):
        """워커 함수"""
        scheduler = NewsScheduler(
            keywords=[keyword],
            interval_seconds=interval_seconds,
            output_file=output_file,
            config_path=config_path,
            use_async=False,
        )
        scheduler.run()
    
    logger.info(f"멀티프로세싱 모드 시작: {num_processes}개 프로세스")
    
    # 키워드를 프로세스에 분배
    processes = []
    for i, keyword in enumerate(keywords):
        p = mp.Process(target=worker, args=(keyword,))
        p.start()
        processes.append(p)
    
    # 종료 신호 처리
    def signal_handler(sig, frame):
        logger.info("종료 신호 수신")
        for p in processes:
            p.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 프로세스 대기
    for p in processes:
        p.join()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="뉴스 수집 스케줄러",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        required=True,
        help="수집할 키워드 리스트",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        choices=[30, 60, 300],
        help="수집 간격 (초): 30, 60, 300",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/news.jsonl",
        help="출력 파일 경로",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config_api.yaml",
        help="설정 파일 경로",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="async",
        choices=["sync", "async", "multiprocess"],
        help="실행 모드: sync, async, multiprocess",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=2,
        help="멀티프로세싱 모드에서 사용할 프로세스 개수",
    )
    
    args = parser.parse_args()
    
    if args.mode == "multiprocess":
        run_multiprocess(
            keywords=args.keywords,
            interval_seconds=args.interval,
            output_file=args.output,
            config_path=args.config,
            num_processes=args.processes,
        )
    else:
        scheduler = NewsScheduler(
            keywords=args.keywords,
            interval_seconds=args.interval,
            output_file=args.output,
            config_path=args.config,
            use_async=(args.mode == "async"),
        )
        
        # 종료 신호 처리
        def signal_handler(sig, frame):
            logger.info("종료 신호 수신")
            scheduler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        scheduler.run()


if __name__ == "__main__":
    import logging
    main()

