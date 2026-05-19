"""
OCR 엔진: Surya 기반

Surya는 레이아웃 감지(텍스트 영역 + 읽기 순서) + OCR을 통합 제공.
한국어 지원, GPU 가속.

설치: pip install surya-ocr
"""
from pathlib import Path
from typing import List
from PIL import Image


class SuryaOCREngine:
    LANGS = ["ko"]  # 한국어

    def __init__(self):
        self._loaded = False
        self.det_model = None
        self.det_processor = None
        self.rec_model = None
        self.rec_processor = None
        self.layout_model = None
        self.layout_processor = None

    def load(self):
        if self._loaded:
            return

        try:
            from surya.model.detection.model import load_model as load_det, load_processor as load_det_proc
            from surya.model.recognition.model import load_model as load_rec
            from surya.model.recognition.processor import load_processor as load_rec_proc
            from surya.model.layout.model import load_model as load_layout
            from surya.model.layout.processor import load_processor as load_layout_proc
        except ImportError:
            raise ImportError("surya-ocr 미설치. 실행: pip install surya-ocr")

        print("Surya 모델 로딩...")
        self.det_model, self.det_processor = load_det(), load_det_proc()
        self.rec_model, self.rec_processor = load_rec(), load_rec_proc()
        self.layout_model, self.layout_processor = load_layout(), load_layout_proc()
        self._loaded = True
        print("Surya 로드 완료")

    def run(self, image_path: str) -> List[dict]:
        """
        이미지 1장 OCR.
        반환: [{"text": str, "bbox": [x1,y1,x2,y2], "confidence": float, "order": int}]
        """
        if not self._loaded:
            raise RuntimeError("load() 먼저 호출하세요")

        from surya.ocr import run_ocr
        from surya.layout import run_layout_detection

        image = Image.open(image_path).convert("RGB")

        # 레이아웃 감지 (텍스트 블록 + 읽기 순서)
        layout_result = run_layout_detection(
            [image], [self.LANGS], self.layout_model, self.layout_processor
        )[0]

        # OCR
        ocr_result = run_ocr(
            [image], [self.LANGS], self.det_model, self.det_processor,
            self.rec_model, self.rec_processor
        )[0]

        return self._merge(ocr_result, layout_result)

    def _merge(self, ocr_result, layout_result) -> List[dict]:
        """OCR 결과와 레이아웃 읽기 순서를 합쳐 정렬된 블록 리스트 반환."""
        blocks = []
        for line in ocr_result.text_lines:
            blocks.append({
                "text": line.text,
                "bbox": line.bbox,
                "confidence": round(line.confidence, 3),
                "order": self._get_reading_order(line.bbox, layout_result),
            })

        # 읽기 순서로 정렬
        blocks.sort(key=lambda b: b["order"])
        return blocks

    def _get_reading_order(self, bbox, layout_result) -> int:
        """텍스트 라인의 bbox가 속한 레이아웃 블록의 읽기 순서 반환."""
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2

        for i, block in enumerate(layout_result.bboxes):
            bx1, by1, bx2, by2 = block.bbox
            if bx1 <= cx <= bx2 and by1 <= cy <= by2:
                return i * 1000 + int(cy)

        # 레이아웃 블록에 속하지 않으면 y좌표로 fallback
        return int(cy) * 10000 + int(bbox[0])
