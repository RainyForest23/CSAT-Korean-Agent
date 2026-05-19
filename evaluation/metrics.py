"""
평가 파이프라인

자동 평가 지표:
- BERTScore: 생성 해설 vs 강민철 원본 해설 의미 유사도
- Style Score: 강민철 특유 표현 패턴 포함 비율
- Coverage Score: 정답 근거 + 오답 근거 커버리지
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class EvaluationResult:
    bert_score: Optional[float] = None
    style_score: Optional[float] = None
    coverage_score: Optional[float] = None
    overall: Optional[float] = None


def evaluate(generated: str, reference: str) -> EvaluationResult:
    raise NotImplementedError


def style_score(generated: str) -> float:
    """강민철 특유 표현 패턴 포함 비율"""
    STYLE_PATTERNS = [
        "이 문제의 포인트는",
        "자, 보면요",
        "여기서 핵심은",
        "이 선지가 틀린 이유는",
        "지문에서 보면",
        "출제 의도는",
    ]
    matches = sum(1 for p in STYLE_PATTERNS if p in generated)
    return matches / len(STYLE_PATTERNS)
