#!/usr/bin/env python3
"""
01_ocr: 강민철 교재 스캔본 OCR 파이프라인

Surya 기반 오픈소스 OCR + 레이아웃 분석.
PDF 또는 이미지 폴더를 입력받아 페이지별 텍스트 JSON을 출력.

Usage:
    python run_ocr.py input.pdf --output data/ocr/
    python run_ocr.py input_dir/ --output data/ocr/ --ext jpg
    python run_ocr.py input.pdf --output data/ocr/ --pages 1-10
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional

from pdf_to_images import pdf_to_images
from ocr_engine import SuryaOCREngine
from postprocess import postprocess_page


def parse_page_range(s: Optional[str], total: int) -> List[int]:
    if not s:
        return list(range(total))
    result = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            result.extend(range(int(a) - 1, int(b)))
        else:
            result.append(int(part) - 1)
    return [i for i in result if 0 <= i < total]


def run(input_path: str, output_dir: str, pages: Optional[str] = None, ext: str = "pdf"):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 이미지 수집
    if input_path.is_dir():
        image_paths = sorted(input_path.glob(f"*.{ext}"))
        print(f"이미지 {len(image_paths)}장 발견: {input_path}")
    elif input_path.suffix.lower() == ".pdf":
        print(f"PDF → 이미지 변환: {input_path}")
        image_paths = pdf_to_images(input_path, output_dir / "images")
        print(f"변환 완료: {len(image_paths)}페이지")
    else:
        print(f"Error: 지원하지 않는 형식 ({input_path.suffix}). PDF 또는 이미지 디렉토리를 입력하세요.")
        sys.exit(1)

    if not image_paths:
        print("Error: 처리할 이미지 없음")
        sys.exit(1)

    # 2. 페이지 범위 필터
    selected = parse_page_range(pages, len(image_paths))
    image_paths = [image_paths[i] for i in selected]
    print(f"처리 대상: {len(image_paths)}페이지")

    # 3. OCR 엔진 로드
    engine = SuryaOCREngine()
    engine.load()

    # 4. 페이지별 OCR
    results = []
    for i, img_path in enumerate(image_paths, 1):
        print(f"  [{i}/{len(image_paths)}] {img_path.name}", end="\r", flush=True)

        raw = engine.run(str(img_path))
        cleaned = postprocess_page(raw)

        page_result = {
            "page": selected[i - 1] + 1,
            "image": str(img_path),
            "blocks": cleaned,
            "full_text": "\n".join(b["text"] for b in cleaned if b["text"].strip()),
        }
        results.append(page_result)

    print(f"\nOCR 완료: {len(results)}페이지")

    # 5. 저장
    book_name = input_path.stem
    out_file = output_dir / f"{book_name}_ocr.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"source": str(input_path), "pages": results}, f, ensure_ascii=False, indent=2)

    print(f"저장: {out_file}")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="교재 스캔본 OCR")
    parser.add_argument("input", help="PDF 파일 또는 이미지 디렉토리")
    parser.add_argument("--output", default="../../data/ocr", help="출력 디렉토리 (기본: data/ocr/)")
    parser.add_argument("--pages", help="처리할 페이지 범위 (예: 1-10,15,20-25)")
    parser.add_argument("--ext", default="jpg", help="이미지 디렉토리 입력 시 확장자 (기본: jpg)")
    args = parser.parse_args()

    run(args.input, args.output, pages=args.pages, ext=args.ext)


if __name__ == "__main__":
    main()
