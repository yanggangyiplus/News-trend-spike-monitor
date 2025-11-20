"""
감정 분석 모듈
HuggingFace Transformers 기반 감정 분석
KcELECTRA와 bert-base-multilingual 지원
"""

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Union, Optional
import logging
import time

from src.nlp.model_optimizer import ModelOptimizer

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """감정 분석기 클래스"""
    
    def __init__(
        self,
        model_name: str = "beomi/KcELECTRA-base",
        device: Optional[str] = None,
    ):
        """
        감정 분석기 초기화
        
        Args:
            model_name: HuggingFace 모델 이름
                - "beomi/KcELECTRA-base": 한국어 최적화
                - "bert-base-multilingual-cased": 다국어 지원
            device: 사용할 디바이스 ('cuda', 'cpu', 'mps', None=자동 선택)
        """
        self.model_name = model_name
        
        # 디바이스 자동 선택
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        self.device = device
        self.model_name = model_name
        self.optimizer: Optional[ModelOptimizer] = None
        self.is_warmed_up = False
        
        # 디바이스 인덱스 설정 (cuda만)
        device_index = 0 if device == "cuda" else -1
        
        try:
            # 감정 분석 파이프라인 초기화
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=device_index,
                return_all_scores=True,
            )
            logger.info(f"감정 분석기 초기화 완료: {model_name} (device: {device})")
            
            # 모델 최적화기 초기화 (선택적)
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.optimizer = ModelOptimizer(model, tokenizer, model_name)
            except Exception as e:
                logger.warning(f"모델 최적화기 초기화 실패 (선택적 기능): {e}")
        
        except Exception as e:
            logger.warning(f"모델 로드 실패, 기본 모델 사용: {e}")
            # 기본 모델로 폴백
            try:
                self.analyzer = pipeline(
                    "sentiment-analysis",
                    device=device_index,
                    return_all_scores=True,
                )
            except Exception as e2:
                logger.error(f"기본 모델 로드도 실패: {e2}")
                raise
    
    def warm_up(self, sample_texts: Optional[List[str]] = None):
        """
        모델 warm-up 수행
        
        Args:
            sample_texts: 샘플 텍스트 리스트
        """
        if self.is_warmed_up:
            logger.info("모델이 이미 warm-up되었습니다.")
            return
        
        if sample_texts is None:
            sample_texts = [
                "This is a positive text.",
                "This is a negative text.",
                "안녕하세요. 긍정적인 텍스트입니다.",
                "안녕하세요. 부정적인 텍스트입니다.",
            ]
        
        logger.info("모델 warm-up 시작...")
        start_time = time.time()
        
        for text in sample_texts:
            try:
                _ = self.analyze(text)
            except Exception as e:
                logger.warning(f"Warm-up 중 오류: {e}")
        
        elapsed = time.time() - start_time
        self.is_warmed_up = True
        logger.info(f"모델 warm-up 완료 ({elapsed:.2f}초)")
    
    def analyze_batch_optimized(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, float]]:
        """
        배치 최적화된 감정 분석
        
        Args:
            texts: 분석할 텍스트 리스트
            batch_size: 배치 크기
            
        Returns:
            감정 점수 리스트
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self._analyze_batch(batch)
            results.extend(batch_results)
        
        return results
    
    def get_top_k_probabilities(self, text: str, top_k: int = 3) -> List[Dict[str, float]]:
        """
        Top-K 확률 반환
        
        Args:
            text: 분석할 텍스트
            top_k: 상위 K개
            
        Returns:
            Top-K 확률 리스트
        """
        sentiment = self.analyze(text)
        
        # 확률값 정렬
        probs = [
            {"label": "positive", "score": sentiment.get("positive", 0.0)},
            {"label": "negative", "score": sentiment.get("negative", 0.0)},
            {"label": "neutral", "score": sentiment.get("neutral", 0.0)},
        ]
        
        probs.sort(key=lambda x: x["score"], reverse=True)
        return probs[:top_k]
    
    def get_gpu_memory_info(self) -> Dict:
        """
        GPU 메모리 사용량 정보 반환
        
        Returns:
            GPU 메모리 정보 딕셔너리
        """
        if self.optimizer:
            return self.optimizer.get_gpu_memory_usage()
        else:
            return {"gpu_available": torch.cuda.is_available()}
    
    def analyze(self, text: Union[str, List[str]]) -> Union[Dict[str, float], List[Dict[str, float]]]:
        """
        텍스트 감정 분석
        
        Args:
            text: 분석할 텍스트 (문자열 또는 문자열 리스트)
            
        Returns:
            감정 점수 딕셔너리 또는 리스트
            {'positive': 0.8, 'negative': 0.2, 'confidence': 0.8}
        """
        if isinstance(text, str):
            return self._analyze_single(text)
        else:
            return self._analyze_batch(text)
    
    def _analyze_single(self, text: str) -> Dict[str, float]:
        """
        단일 텍스트 감정 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감정 점수 딕셔너리
        """
        if not text or len(text.strip()) == 0:
            return {
                "positive": 0.5,
                "negative": 0.5,
                "neutral": 0.0,
                "confidence": 0.0,
            }
        
        try:
            # 파이프라인 실행
            results = self.analyzer(text)
            
            # 결과 파싱
            if isinstance(results, list) and len(results) > 0:
                # return_all_scores=True인 경우
                scores = results[0] if isinstance(results[0], list) else results
                
                # 라벨과 점수 추출
                sentiment_dict = {}
                max_score = 0.0
                
                for item in scores:
                    if isinstance(item, dict):
                        label = item.get("label", "").lower()
                        score = item.get("score", 0.0)
                        sentiment_dict[label] = score
                        max_score = max(max_score, score)
                
                # 라벨 정규화 (다양한 모델 대응)
                positive_score = 0.5
                negative_score = 0.5
                neutral_score = 0.0
                
                # 긍정 라벨 찾기
                for key in ["positive", "pos", "긍정", "positive_1"]:
                    if key in sentiment_dict:
                        positive_score = sentiment_dict[key]
                        break
                
                # 부정 라벨 찾기
                for key in ["negative", "neg", "부정", "negative_1"]:
                    if key in sentiment_dict:
                        negative_score = sentiment_dict[key]
                        break
                
                # 중립 라벨 찾기
                for key in ["neutral", "neu", "중립"]:
                    if key in sentiment_dict:
                        neutral_score = sentiment_dict[key]
                        break
                
                # 정규화 (합이 1이 되도록)
                total = positive_score + negative_score + neutral_score
                if total > 0:
                    positive_score /= total
                    negative_score /= total
                    neutral_score /= total
                
                return {
                    "positive": float(positive_score),
                    "negative": float(negative_score),
                    "neutral": float(neutral_score),
                    "confidence": float(max_score),
                }
            
            else:
                # 단일 결과인 경우
                if isinstance(results, dict):
                    label = results.get("label", "").lower()
                    score = results.get("score", 0.5)
                    
                    if "positive" in label or "pos" in label:
                        return {
                            "positive": float(score),
                            "negative": float(1 - score),
                            "neutral": 0.0,
                            "confidence": float(score),
                        }
                    elif "negative" in label or "neg" in label:
                        return {
                            "positive": float(1 - score),
                            "negative": float(score),
                            "neutral": 0.0,
                            "confidence": float(score),
                        }
                    else:
                        return {
                            "positive": 0.5,
                            "negative": 0.5,
                            "neutral": float(score),
                            "confidence": float(score),
                        }
        
        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return {
                "positive": 0.5,
                "negative": 0.5,
                "neutral": 0.0,
                "confidence": 0.0,
            }
    
    def _analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        배치 감정 분석
        
        Args:
            texts: 분석할 텍스트 리스트
            
        Returns:
            감정 점수 리스트
        """
        results = []
        
        for text in texts:
            result = self._analyze_single(text)
            results.append(result)
        
        return results
    
    def get_sentiment_score(self, text: str) -> float:
        """
        감정 점수 계산 (0~1, 1에 가까울수록 긍정)
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감정 점수 (0.0 ~ 1.0)
        """
        sentiment = self.analyze(text)
        return sentiment.get("positive", 0.5)
    
    def get_confidence(self, text: str) -> float:
        """
        감정 분석 신뢰도 반환
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            신뢰도 (0.0 ~ 1.0)
        """
        sentiment = self.analyze(text)
        return sentiment.get("confidence", 0.0)
