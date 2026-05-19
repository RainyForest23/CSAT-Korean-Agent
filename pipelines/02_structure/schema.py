"""
구조화 출력 스키마

OCR 결과 → (지문, 문제, 선지, 정답, 해설) 단위로 변환.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class Question:
    number: int
    stem: str                          # 문제 본문
    options: List[str]                 # 선지 ①②③④⑤
    answer: Optional[str] = None       # 정답 번호
    commentary: Optional[str] = None   # 강민철 해설


@dataclass
class PassageItem:
    id: str                            # 예: "문학_001"
    source_page: int                   # 원본 페이지 번호
    genre: Optional[str] = None        # 현대시/현대소설/고전시가/고전소설/독서
    passage: Optional[str] = None      # 지문 전문
    questions: List[Question] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        return d


@dataclass
class StructuredBook:
    source_ocr: str                    # 원본 OCR JSON 경로
    items: List[PassageItem] = field(default_factory=list)

    def to_dict(self):
        return {
            "source_ocr": self.source_ocr,
            "items": [item.to_dict() for item in self.items],
        }

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @property
    def stats(self) -> dict:
        total_q = sum(len(item.questions) for item in self.items)
        with_commentary = sum(
            1 for item in self.items
            for q in item.questions if q.commentary
        )
        return {
            "passages": len(self.items),
            "questions": total_q,
            "with_commentary": with_commentary,
            "coverage": round(with_commentary / total_q, 3) if total_q else 0,
        }
