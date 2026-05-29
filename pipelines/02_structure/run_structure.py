#!/usr/bin/env python3
"""
02_structure: Markdown → (지문/문제/선지/정답/해설) 구조화

01_parse에서 생성된 data/markdown/ 의 .md 파일을 입력으로 받아
(지문, 문제, 선지, 정답, 해설) JSON으로 구조화.

Usage:
    # data/markdown/ 전체 일괄 처리 (기본)
    python run_structure.py

    # 단일 파일
    python run_structure.py ../../data/markdown/강민철_문학/강민철_문학.md

    # 이어서 처리
    python run_structure.py --resume

    # 샘플 테스트 (처음 N 청크만)
    python run_structure.py --sample 5

    # 로컬 모델 경로 지정 (서버)
    python run_structure.py --model /path/to/exaone
"""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractor import ExaoneExtractor, dict_to_passage_item
from schema import StructuredBook
from validate import validate_all, print_report

MARKDOWN_DIR = Path(__file__).resolve().parents[2] / "data" / "markdown"
STRUCTURED_DIR = Path(__file__).resolve().parents[2] / "data" / "structured"

# 지문+문제+해설이 포함될 Markdown 청크 크기 (문자 수)
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 500


def chunk_markdown(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Markdown을 헤딩(#, ##) 기준으로 청킹.
    헤딩이 없는 경우 문자 수 기준으로 분할.
    """
    import re
    # ## 또는 # 헤딩 기준으로 섹션 분리
    sections = re.split(r"(?=^#{1,2} )", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    chunks = []
    buffer = ""
    for section in sections:
        if len(buffer) + len(section) <= chunk_size:
            buffer += "\n\n" + section
        else:
            if buffer:
                chunks.append({"text": buffer.strip(), "start_char": 0})
            buffer = section

    if buffer:
        chunks.append({"text": buffer.strip(), "start_char": 0})

    return chunks if chunks else [{"text": text[:chunk_size], "start_char": 0}]


def process_file(
    md_path: Path,
    output_dir: Path,
    extractor: ExaoneExtractor,
    sample: int = 0,
    resume: bool = False,
) -> Path:
    out_path = output_dir / (md_path.stem + "_structured.json")

    if resume and out_path.exists():
        print(f"건너뜀 (완료): {md_path.name}")
        return out_path

    text = md_path.read_text(encoding="utf-8")
    chunks = chunk_markdown(text)

    if sample:
        chunks = chunks[:sample]

    book = StructuredBook(source_ocr=str(md_path))
    item_counter = 1

    print(f"\n{md_path.name}: {len(chunks)}개 청크")

    for i, chunk in enumerate(chunks, 1):
        print(f"  [{i}/{len(chunks)}] 구조화 중...", end="\r", flush=True)

        result = extractor.extract(chunk["text"])
        if result is None:
            print(f"\n  경고: 청크 {i} 구조화 실패, 건너뜀")
            continue

        # 지문이나 문제가 없는 청크는 스킵 (목차, 머리말 등)
        if not result.get("passage") and not result.get("questions"):
            continue

        item_id = f"{md_path.stem}_{item_counter:04d}"
        item = dict_to_passage_item(result, item_id=item_id, page=i)
        book.items.append(item)
        item_counter += 1

    print(f"\n완료: {len(book.items)}개 항목 추출")

    output_dir.mkdir(parents=True, exist_ok=True)
    book.save(str(out_path))
    print(f"저장: {out_path}")

    report = validate_all(book.items)
    print_report(report)

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Markdown 교재 구조화")
    parser.add_argument(
        "input", nargs="?", default=str(MARKDOWN_DIR),
        help="Markdown 파일 또는 디렉토리 (기본: data/markdown/)"
    )
    parser.add_argument("--output", default=str(STRUCTURED_DIR), help="출력 디렉토리")
    parser.add_argument("--model", default="LGAI-EXAONE/EXAONE-4.0.1-32B", help="EXAONE 모델 경로")
    parser.add_argument("--sample", type=int, default=0, help="테스트용 청크 수 제한 (0=전체)")
    parser.add_argument("--resume", action="store_true", help="이미 완료된 파일 건너뜀")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if input_path.is_dir():
        files = sorted(input_path.rglob("*.md"))
    elif input_path.suffix == ".md":
        files = [input_path]
    else:
        print("Error: .md 파일 또는 디렉토리를 입력하세요.")
        sys.exit(1)

    if not files:
        print(f"처리할 Markdown 파일 없음 — {input_path}")
        sys.exit(1)

    print(f"처리 대상: {len(files)}개 파일")

    extractor = ExaoneExtractor(model_path=args.model)
    extractor.load()

    for f in files:
        process_file(f, output_dir, extractor, sample=args.sample, resume=args.resume)

    print("\n전체 완료")


if __name__ == "__main__":
    main()
