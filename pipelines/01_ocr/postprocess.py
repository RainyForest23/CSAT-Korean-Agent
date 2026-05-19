"""
OCR 후처리

- 낮은 confidence 블록 필터링
- 페이지 번호 / 헤더 / 푸터 제거
- 하이픈 이어쓰기 복원
- 특수문자 정제
"""
import re
from typing import List

CONFIDENCE_THRESHOLD = 0.6

# 교재에서 제거할 패턴 (페이지 번호, 저작권 등)
NOISE_PATTERNS = [
    r"^\d{1,3}$",                      # 단독 페이지 번호
    r"^www\.",                          # URL
    r"^Copyright",
    r"^시대인재|^강민철|^EBS|^수능특강",  # 표지/헤더
]


def postprocess_page(blocks: List[dict]) -> List[dict]:
    result = []
    for block in blocks:
        if block["confidence"] < CONFIDENCE_THRESHOLD:
            continue
        text = _clean_text(block["text"])
        if not text or _is_noise(text):
            continue
        block["text"] = text
        result.append(block)
    return result


def _clean_text(text: str) -> str:
    # 하이픈 이어쓰기 복원 (줄 끝 하이픈)
    text = re.sub(r"-\s+", "", text)
    # 불필요한 공백 정리
    text = re.sub(r"\s{2,}", " ", text)
    # 특수문자 정제 (OCR 오인식 공통 패턴)
    text = text.replace("ㅣ", "l").replace("０", "0")
    return text.strip()


def _is_noise(text: str) -> bool:
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, text):
            return True
    return False
