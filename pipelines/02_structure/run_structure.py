#!/usr/bin/env python3
"""
02_structure: OCR JSON → (지문/문제/선지/정답/해설) 구조화

Usage:
    # 단일 파일
    python run_structure.py ../../data/ocr/강민철_문학_ocr.json

    # 디렉토리 전체 (일괄 처리)
    python run_structure.py ../../data/ocr/ --output ../../data/structured/

    # 이어서 처리 (이미 완료된 파일 건너뜀)
    python run_structure.py ../../data/ocr/ --resume

    # 샘플 테스트 (처음 N 페이지만)
    python run_structure.py ../../data/ocr/강민철_문학_ocr.json --sample 10
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractor import ExaoneExtractor, dict_to_passage_item
from schema import StructuredBook
from validate import validate_all, print_report


def process_file(
    ocr_json_path: Path,
    output_dir: Path,
    extractor: ExaoneExtractor,
    sample: int = 0,
    resume: bool = False,
) -> Path:
    out_path = output_dir / ocr_json_path.name.replace("_ocr.json", "_structured.json")

    if resume and out_path.exists():
        print(f"건너뜀 (이미 완료): {ocr_json_path.name}")
        return out_path

    with open(ocr_json_path, encoding="utf-8") as f:
        ocr_data = json.load(f)

    pages = ocr_data.get("pages", [])
    if sample:
        pages = pages[:sample]

    book = StructuredBook(source_ocr=str(ocr_json_path))
    item_counter = 1

    # 페이지 그룹핑: 연속된 페이지를 묶어서 LLM에 전달
    # 교재 특성상 지문+문제+해설이 2-4페이지에 걸쳐 있음
    page_groups = _group_pages(pages, window=3)

    print(f"\n{ocr_json_path.name}: {len(pages)}페이지 → {len(page_groups)}개 그룹")

    for i, group in enumerate(page_groups, 1):
        combined_text = "\n\n".join(p["full_text"] for p in group)
        page_nums = [p["page"] for p in group]

        print(f"  [{i}/{len(page_groups)}] 페이지 {page_nums} 구조화 중...", end="\r", flush=True)

        result = extractor.extract(combined_text)
        if result is None:
            print(f"\n  경고: 페이지 {page_nums} 구조화 실패, 건너뜀")
            continue

        item_id = f"{ocr_json_path.stem}_{item_counter:04d}"
        item = dict_to_passage_item(result, item_id=item_id, page=page_nums[0])
        book.items.append(item)
        item_counter += 1

    print(f"\n완료: {len(book.items)}개 항목 추출")

    # 저장
    output_dir.mkdir(parents=True, exist_ok=True)
    book.save(str(out_path))
    print(f"저장: {out_path}")

    # QA
    report = validate_all(book.items)
    print_report(report)

    return out_path


def _group_pages(pages: list, window: int = 3) -> list:
    """
    페이지를 window 크기 슬라이딩으로 묶기.
    지문+문제+해설이 여러 페이지에 걸치는 경우를 처리.
    중복 없이 non-overlapping 그룹으로 분할.
    """
    groups = []
    i = 0
    while i < len(pages):
        groups.append(pages[i:i + window])
        i += window
    return groups


def main():
    parser = argparse.ArgumentParser(description="OCR 결과 구조화")
    parser.add_argument("input", help="OCR JSON 파일 또는 디렉토리 (data/ocr/)")
    parser.add_argument("--output", default="../../data/structured", help="출력 디렉토리")
    parser.add_argument("--model", default="LGAI-EXAONE/EXAONE-4.0.1-32B", help="EXAONE 모델 경로")
    parser.add_argument("--sample", type=int, default=0, help="테스트용 페이지 수 제한 (0=전체)")
    parser.add_argument("--resume", action="store_true", help="이미 완료된 파일 건너뜀")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if input_path.is_dir():
        files = sorted(input_path.glob("*_ocr.json"))
    elif input_path.suffix == ".json":
        files = [input_path]
    else:
        print(f"Error: JSON 파일 또는 디렉토리를 입력하세요.")
        sys.exit(1)

    if not files:
        print("처리할 OCR JSON 파일 없음")
        sys.exit(1)

    print(f"처리 대상: {len(files)}개 파일")

    extractor = ExaoneExtractor(model_path=args.model)
    extractor.load()

    for f in files:
        process_file(f, output_dir, extractor, sample=args.sample, resume=args.resume)

    print("\n전체 완료")


if __name__ == "__main__":
    main()
