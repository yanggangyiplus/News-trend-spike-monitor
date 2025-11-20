"""
데이터 저장 유틸리티
Parquet, DeltaLake, S3 업로드 기능
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataStorage:
    """데이터 저장 클래스"""
    
    def __init__(self, base_path: str = "data"):
        """
        데이터 저장소 초기화
        
        Args:
            base_path: 기본 저장 경로
        """
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "database" / "news_raw.jsonl"
        self.clean_path = self.base_path / "database" / "news_clean.jsonl"
        self.sentiment_path = self.base_path / "database" / "sentiment.parquet"
        self.spikes_path = self.base_path / "database" / "spikes.parquet"
        
        # 디렉토리 생성
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "database").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"데이터 저장소 초기화 완료: {self.base_path}")
    
    def save_raw_news(self, news_items: List[Dict]):
        """
        원본 뉴스 데이터를 JSONL 형식으로 저장
        
        Args:
            news_items: 뉴스 아이템 리스트
        """
        try:
            with open(self.raw_path, "a", encoding="utf-8") as f:
                for item in news_items:
                    json.dump(item, f, ensure_ascii=False)
                    f.write("\n")
            
            logger.info(f"원본 뉴스 {len(news_items)}개 저장 완료: {self.raw_path}")
        
        except Exception as e:
            logger.error(f"원본 뉴스 저장 오류: {e}")
            raise
    
    def save_clean_news(self, news_items: List[Dict]):
        """
        전처리된 뉴스 데이터를 JSONL 형식으로 저장
        
        Args:
            news_items: 전처리된 뉴스 아이템 리스트
        """
        try:
            with open(self.clean_path, "a", encoding="utf-8") as f:
                for item in news_items:
                    json.dump(item, f, ensure_ascii=False)
                    f.write("\n")
            
            logger.info(f"전처리 뉴스 {len(news_items)}개 저장 완료: {self.clean_path}")
        
        except Exception as e:
            logger.error(f"전처리 뉴스 저장 오류: {e}")
            raise
    
    def save_sentiment_data(self, sentiment_data: List[Dict]):
        """
        감정 분석 데이터를 Parquet 형식으로 저장
        
        Args:
            sentiment_data: 감정 분석 데이터 리스트
        """
        try:
            if not sentiment_data:
                return
            
            df = pd.DataFrame(sentiment_data)
            
            # 기존 파일이 있으면 병합
            if self.sentiment_path.exists():
                existing_df = pd.read_parquet(self.sentiment_path)
                df = pd.concat([existing_df, df], ignore_index=True)
                # 중복 제거 (타임스탬프 기준)
                df = df.drop_duplicates(subset=["timestamp", "keyword"], keep="last")
            
            # Parquet로 저장
            df.to_parquet(self.sentiment_path, index=False, engine="pyarrow")
            
            logger.info(f"감정 분석 데이터 {len(sentiment_data)}개 저장 완료: {self.sentiment_path}")
        
        except Exception as e:
            logger.error(f"감정 분석 데이터 저장 오류: {e}")
            raise
    
    def save_spikes_data(self, spikes_data: List[Dict]):
        """
        스파이크 데이터를 Parquet 형식으로 저장
        
        Args:
            spikes_data: 스파이크 데이터 리스트
        """
        try:
            if not spikes_data:
                return
            
            df = pd.DataFrame(spikes_data)
            
            # 기존 파일이 있으면 병합
            if self.spikes_path.exists():
                existing_df = pd.read_parquet(self.spikes_path)
                df = pd.concat([existing_df, df], ignore_index=True)
                # 중복 제거
                df = df.drop_duplicates(subset=["timestamp", "keyword"], keep="last")
            
            # Parquet로 저장
            df.to_parquet(self.spikes_path, index=False, engine="pyarrow")
            
            logger.info(f"스파이크 데이터 {len(spikes_data)}개 저장 완료: {self.spikes_path}")
        
        except Exception as e:
            logger.error(f"스파이크 데이터 저장 오류: {e}")
            raise
    
    def load_sentiment_data(
        self,
        keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        감정 분석 데이터 로드
        
        Args:
            keyword: 키워드 필터
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            감정 분석 데이터프레임
        """
        try:
            if not self.sentiment_path.exists():
                return pd.DataFrame()
            
            df = pd.read_parquet(self.sentiment_path)
            
            # 필터링
            if keyword:
                df = df[df["keyword"] == keyword]
            
            if start_date:
                df = df[pd.to_datetime(df["timestamp"]) >= start_date]
            
            if end_date:
                df = df[pd.to_datetime(df["timestamp"]) <= end_date]
            
            return df
        
        except Exception as e:
            logger.error(f"감정 분석 데이터 로드 오류: {e}")
            return pd.DataFrame()
    
    def load_spikes_data(
        self,
        keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        스파이크 데이터 로드
        
        Args:
            keyword: 키워드 필터
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            스파이크 데이터프레임
        """
        try:
            if not self.spikes_path.exists():
                return pd.DataFrame()
            
            df = pd.read_parquet(self.spikes_path)
            
            # 필터링
            if keyword:
                df = df[df["keyword"] == keyword]
            
            if start_date:
                df = df[pd.to_datetime(df["timestamp"]) >= start_date]
            
            if end_date:
                df = df[pd.to_datetime(df["timestamp"]) <= end_date]
            
            return df
        
        except Exception as e:
            logger.error(f"스파이크 데이터 로드 오류: {e}")
            return pd.DataFrame()


class S3Storage:
    """S3 저장 클래스 (선택적)"""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = "ap-northeast-2",
    ):
        """
        S3 저장소 초기화
        
        Args:
            bucket_name: S3 버킷 이름
            aws_access_key_id: AWS 액세스 키 ID
            aws_secret_access_key: AWS 시크릿 액세스 키
            region: AWS 리전
        """
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = None
        
        # boto3는 선택적 의존성
        try:
            import boto3
            if aws_access_key_id and aws_secret_access_key:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region,
                )
            else:
                # 환경 변수 또는 IAM 역할 사용
                self.s3_client = boto3.client("s3", region_name=region)
            
            logger.info(f"S3 저장소 초기화 완료: {bucket_name}")
        
        except ImportError:
            logger.warning("boto3가 설치되지 않았습니다. S3 기능을 사용할 수 없습니다.")
        except Exception as e:
            logger.warning(f"S3 초기화 실패: {e}")
    
    def upload_file(self, local_path: str, s3_key: str):
        """
        파일을 S3에 업로드
        
        Args:
            local_path: 로컬 파일 경로
            s3_key: S3 키 (경로)
        """
        if not self.s3_client:
            logger.warning("S3 클라이언트가 초기화되지 않았습니다.")
            return
        
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"파일 업로드 완료: {local_path} -> s3://{self.bucket_name}/{s3_key}")
        
        except Exception as e:
            logger.error(f"S3 업로드 오류: {e}")
            raise
    
    def upload_parquet(self, df: pd.DataFrame, s3_key: str):
        """
        DataFrame을 Parquet 형식으로 S3에 업로드
        
        Args:
            df: 데이터프레임
            s3_key: S3 키 (경로)
        """
        if not self.s3_client:
            logger.warning("S3 클라이언트가 초기화되지 않았습니다.")
            return
        
        try:
            import io
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False, engine="pyarrow")
            buffer.seek(0)
            
            self.s3_client.upload_fileobj(buffer, self.bucket_name, s3_key)
            logger.info(f"Parquet 업로드 완료: s3://{self.bucket_name}/{s3_key}")
        
        except Exception as e:
            logger.error(f"S3 Parquet 업로드 오류: {e}")
            raise

