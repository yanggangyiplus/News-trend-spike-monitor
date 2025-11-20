#!/usr/bin/env python3
"""
데이터 저장 성능 벤치마크 스크립트
"""

import sys
import time
import json
import tempfile
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("pandas 또는 pyarrow가 설치되지 않았습니다.")
    print("설치: pip install pandas pyarrow")
    sys.exit(1)


def generate_sample_data(n=1000):
    """
    샘플 데이터 생성
    
    Args:
        n: 생성할 데이터 개수
        
    Returns:
        데이터 리스트
    """
    import random
    
    data = []
    for i in range(n):
        item = {
            "id": i,
            "title": f"뉴스 제목 {i}",
            "summary": f"이것은 샘플 뉴스 내용입니다. " * 10,  # 약 500자
            "link": f"https://example.com/news/{i}",
            "published": "2024-01-01T00:00:00",
            "source": "test",
            "sentiment_score": random.uniform(0, 1),
            "processed_at": "2024-01-01T00:00:00",
        }
        data.append(item)
    
    return data


def benchmark_jsonl(data: list, output_path: Path):
    """JSONL 형식 벤치마크"""
    start_time = time.time()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    write_time = time.time() - start_time
    
    # 파일 크기
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    
    # 읽기 테스트
    start_time = time.time()
    with open(output_path, 'r', encoding='utf-8') as f:
        for line in f:
            json.loads(line)
    read_time = time.time() - start_time
    
    return {
        "format": "JSONL",
        "write_time": round(write_time, 2),
        "read_time": round(read_time, 2),
        "file_size_mb": round(file_size, 2),
        "compression_ratio": None,
    }


def benchmark_parquet(data: list, output_path: Path, compression='snappy'):
    """Parquet 형식 벤치마크"""
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # 쓰기 테스트
    start_time = time.time()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path, compression=compression)
    write_time = time.time() - start_time
    
    # 파일 크기
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    
    # 읽기 테스트
    start_time = time.time()
    table = pq.read_table(output_path)
    df_read = table.to_pandas()
    read_time = time.time() - start_time
    
    # 압축률 계산 (JSONL 기준)
    jsonl_size = sum(len(json.dumps(item, ensure_ascii=False)) for item in data) / (1024 * 1024)
    compression_ratio = (1 - file_size / jsonl_size) * 100 if jsonl_size > 0 else 0
    
    return {
        "format": f"Parquet ({compression})",
        "write_time": round(write_time, 2),
        "read_time": round(read_time, 2),
        "file_size_mb": round(file_size, 2),
        "compression_ratio": round(compression_ratio, 1),
    }


def benchmark_csv(data: list, output_path: Path):
    """CSV 형식 벤치마크"""
    df = pd.DataFrame(data)
    
    # 쓰기 테스트
    start_time = time.time()
    df.to_csv(output_path, index=False, encoding='utf-8')
    write_time = time.time() - start_time
    
    # 파일 크기
    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    
    # 읽기 테스트
    start_time = time.time()
    df_read = pd.read_csv(output_path, encoding='utf-8')
    read_time = time.time() - start_time
    
    return {
        "format": "CSV",
        "write_time": round(write_time, 2),
        "read_time": round(read_time, 2),
        "file_size_mb": round(file_size, 2),
        "compression_ratio": None,
    }


def main():
    """메인 함수"""
    print("="*60)
    print("데이터 저장 성능 벤치마크")
    print("="*60)
    
    # 샘플 데이터 생성
    print("\n샘플 데이터 생성 중...")
    data = generate_sample_data(n=1000)
    print(f"생성 완료: {len(data)}개 아이템")
    
    # 임시 디렉토리 생성
    temp_dir = Path(tempfile.mkdtemp())
    print(f"임시 디렉토리: {temp_dir}")
    
    results = []
    
    # JSONL 벤치마크
    print("\n" + "="*60)
    print("JSONL 벤치마크")
    print("="*60)
    jsonl_path = temp_dir / "test.jsonl"
    result = benchmark_jsonl(data, jsonl_path)
    results.append(result)
    print(f"쓰기 시간: {result['write_time']}초")
    print(f"읽기 시간: {result['read_time']}초")
    print(f"파일 크기: {result['file_size_mb']} MB")
    
    # Parquet (snappy) 벤치마크
    print("\n" + "="*60)
    print("Parquet (snappy) 벤치마크")
    print("="*60)
    parquet_snappy_path = temp_dir / "test_snappy.parquet"
    result = benchmark_parquet(data, parquet_snappy_path, compression='snappy')
    results.append(result)
    print(f"쓰기 시간: {result['write_time']}초")
    print(f"읽기 시간: {result['read_time']}초")
    print(f"파일 크기: {result['file_size_mb']} MB")
    print(f"압축률: {result['compression_ratio']}%")
    
    # Parquet (gzip) 벤치마크
    print("\n" + "="*60)
    print("Parquet (gzip) 벤치마크")
    print("="*60)
    parquet_gzip_path = temp_dir / "test_gzip.parquet"
    result = benchmark_parquet(data, parquet_gzip_path, compression='gzip')
    results.append(result)
    print(f"쓰기 시간: {result['write_time']}초")
    print(f"읽기 시간: {result['read_time']}초")
    print(f"파일 크기: {result['file_size_mb']} MB")
    print(f"압축률: {result['compression_ratio']}%")
    
    # CSV 벤치마크
    print("\n" + "="*60)
    print("CSV 벤치마크")
    print("="*60)
    csv_path = temp_dir / "test.csv"
    result = benchmark_csv(data, csv_path)
    results.append(result)
    print(f"쓰기 시간: {result['write_time']}초")
    print(f"읽기 시간: {result['read_time']}초")
    print(f"파일 크기: {result['file_size_mb']} MB")
    
    # 결과 요약
    print("\n" + "="*60)
    print("최종 결과 요약")
    print("="*60)
    
    if results:
        print(f"\n{'형식':<25} {'쓰기(초)':<12} {'읽기(초)':<12} {'크기(MB)':<12} {'압축률(%)':<12}")
        print("-" * 75)
        for r in results:
            compression = f"{r['compression_ratio']}" if r['compression_ratio'] is not None else "-"
            print(f"{r['format']:<25} {r['write_time']:<12} {r['read_time']:<12} {r['file_size_mb']:<12} {compression:<12}")
    
    # 임시 파일 정리
    import shutil
    shutil.rmtree(temp_dir)
    print(f"\n임시 디렉토리 정리 완료: {temp_dir}")
    
    print("\n벤치마크 완료!")
    return results


if __name__ == "__main__":
    main()

