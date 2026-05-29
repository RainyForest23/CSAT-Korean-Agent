#!/usr/bin/env python3
"""
01_parse: 강민철 교재 PDF → Markdown 변환

opendataloader-pdf 기반. 스캔본 포함 모든 PDF를 Markdown으로 변환하여
data/markdown/ 에 지식베이스로 저장.

파이프라인 위치:
    data/pdf/ (스캔본) → [01_parse] → data/markdown/ → [02_structure] → data/structured/

Usage:
    # data/pdf/ 전체 일괄 변환 (기본)
    python run_parse.py

    # 단일 파일
    python run_parse.py ../../data/pdf/강민철_문학.pdf

    # 출력 디렉토리 지정
    python run_parse.py --output ../../data/markdown/

    # 이미 변환된 파일 건너뜀 (이어하기)
    python run_parse.py --resume

Requirements:
    pip install opendataloader-pdf
    Java 11+ 필요 (java -version 으로 확인)
"""

import os
import sys
import argparse
from pathlib import Path

PDF_DIR = Path(__file__).resolve().parents[2] / "data" / "pdf"
MARKDOWN_DIR = Path(__file__).resolve().parents[2] / "data" / "markdown"


def check_java():
    ret = os.system("java -version > /dev/null 2>&1")
    if ret != 0:
        print("Error: Java 11+ 미설치.")
        print("설치: https://adoptium.net/")
        sys.exit(1)


def get_pending_files(pdf_dir: Path, output_dir: Path, resume: bool) -> list[Path]:
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"Error: PDF 파일 없음 — {pdf_dir}")
        sys.exit(1)

    if not resume:
        return pdfs

    # 이미 변환된 파일 건너뜀
    pending = []
    for pdf in pdfs:
        out = output_dir / pdf.stem / f"{pdf.stem}.md"
        if out.exists():
            print(f"  건너뜀 (완료): {pdf.name}")
        else:
            pending.append(pdf)
    return pending


def run(input_path: str, output_dir: Path, resume: bool = False):
    try:
        import opendataloader_pdf
    except ImportError:
        print("Error: opendataloader-pdf 미설치.")
        print("설치: pip install opendataloader-pdf")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(input_path)

    # 입력이 디렉토리면 내부 PDF 전체 처리
    if input_path.is_dir():
        files = get_pending_files(input_path, output_dir, resume)
    elif input_path.suffix.lower() == ".pdf":
        files = [input_path]
    else:
        print(f"Error: PDF 파일 또는 디렉토리를 입력하세요.")
        sys.exit(1)

    if not files:
        print("처리할 파일 없음 (모두 완료됨)")
        return

    print(f"변환 대상: {len(files)}개 PDF")
    print(f"출력 디렉토리: {output_dir}\n")

    # opendataloader-pdf는 배치 처리 권장 (JVM을 1회만 띄움)
    opendataloader_pdf.convert(
        input_path=[str(f) for f in files],
        output_dir=str(output_dir),
        format="markdown,json",   # markdown: 지식베이스 / json: bbox 정보 보존
    )

    print(f"\n변환 완료: {len(files)}개")
    print(f"결과 위치: {output_dir}")
    _print_summary(output_dir, files)


def _print_summary(output_dir: Path, files: list[Path]):
    print(f"\n{'='*50}")
    print("변환 결과 요약")
    print(f"{'='*50}")
    for f in files:
        md_candidates = list(output_dir.rglob(f"{f.stem}*.md"))
        status = "완료" if md_candidates else "실패"
        size = md_candidates[0].stat().st_size // 1024 if md_candidates else 0
        print(f"  {status}  {f.name}  →  {size}KB")


def main():
    parser = argparse.ArgumentParser(description="교재 PDF → Markdown 변환")
    parser.add_argument(
        "input", nargs="?", default=str(PDF_DIR),
        help="PDF 파일 또는 디렉토리 (기본: data/pdf/)"
    )
    parser.add_argument(
        "--output", default=str(MARKDOWN_DIR),
        help="출력 디렉토리 (기본: data/markdown/)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="이미 변환된 파일 건너뜀"
    )
    args = parser.parse_args()

    check_java()
    run(args.input, Path(args.output), resume=args.resume)


if __name__ == "__main__":
    main()
