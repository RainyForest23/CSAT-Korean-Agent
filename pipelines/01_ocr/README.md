# 01_ocr: 교재 스캔본 OCR 파이프라인

## 설치

```bash
pip install -r requirements.txt
```

GPU 사용 권장 (Surya는 CPU도 동작하나 느림).

## 사용법

```bash
# PDF 전체
python run_ocr.py 강민철_문학.pdf --output ../../data/ocr/

# PDF 특정 페이지만
python run_ocr.py 강민철_문학.pdf --output ../../data/ocr/ --pages 1-50

# 이미지 디렉토리
python run_ocr.py scan_images/ --output ../../data/ocr/ --ext png
```

## 출력 형식

`data/ocr/{파일명}_ocr.json`

```json
{
  "source": "강민철_문학.pdf",
  "pages": [
    {
      "page": 1,
      "image": "data/ocr/images/page_0001.png",
      "blocks": [
        {
          "text": "다음 글을 읽고 물음에 답하시오.",
          "bbox": [100, 200, 800, 230],
          "confidence": 0.97,
          "order": 0
        }
      ],
      "full_text": "다음 글을 읽고 물음에 답하시오.\n..."
    }
  ]
}
```

## 파이프라인 흐름

```
PDF / 이미지
  → pdf_to_images.py   (PDF → PNG, pymupdf)
  → ocr_engine.py      (Surya: 레이아웃 감지 + OCR)
  → postprocess.py     (노이즈 제거, 읽기순서 정렬)
  → data/ocr/*.json
```

## 다음 단계

OCR 결과 → `02_structure/` 에서 (지문/문제/해설) 구조화
