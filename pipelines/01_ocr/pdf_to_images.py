"""
PDF → 이미지 변환

pymupdf(fitz) 사용 - poppler 의존성 없이 빠른 변환.
"""
from pathlib import Path
from typing import List

try:
    import fitz  # pymupdf
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


def pdf_to_images(pdf_path: str | Path, output_dir: str | Path, dpi: int = 200) -> List[Path]:
    """
    PDF를 페이지별 이미지로 변환.
    pymupdf 우선, 없으면 pdf2image 사용.
    dpi=200: OCR 품질과 속도의 균형점.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if HAS_FITZ:
        return _convert_with_fitz(pdf_path, output_dir, dpi)
    elif HAS_PDF2IMAGE:
        return _convert_with_pdf2image(pdf_path, output_dir, dpi)
    else:
        raise ImportError("pymupdf 또는 pdf2image 중 하나를 설치하세요: pip install pymupdf")


def _convert_with_fitz(pdf_path: Path, output_dir: Path, dpi: int) -> List[Path]:
    doc = fitz.open(str(pdf_path))
    paths = []
    mat = fitz.Matrix(dpi / 72, dpi / 72)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        out = output_dir / f"page_{page_num + 1:04d}.png"
        pix.save(str(out))
        paths.append(out)

    doc.close()
    return paths


def _convert_with_pdf2image(pdf_path: Path, output_dir: Path, dpi: int) -> List[Path]:
    images = convert_from_path(str(pdf_path), dpi=dpi)
    paths = []
    for i, img in enumerate(images):
        out = output_dir / f"page_{i + 1:04d}.png"
        img.save(str(out), "PNG")
        paths.append(out)
    return paths
