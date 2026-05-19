"""
LLM 기반 구조화 엔진

서버의 EXAONE 32B를 사용하여 OCR 텍스트 → (지문/문제/해설) JSON 추출.
"""
import json
import re
from typing import Optional

from prompts import SYSTEM_PROMPT, build_prompt
from schema import PassageItem, Question

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class ExaoneExtractor:
    """서버의 EXAONE 32B로 구조화 수행."""

    def __init__(self, model_path: str = "LGAI-EXAONE/EXAONE-4.0.1-32B"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        if not HAS_TRANSFORMERS:
            raise ImportError("pip install transformers torch")

        print(f"EXAONE 로딩: {self.model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model.eval()
        self._loaded = True
        print("EXAONE 로드 완료")

    def extract(self, ocr_text: str) -> Optional[dict]:
        """OCR 텍스트 → 구조화 dict. 실패 시 None 반환."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(ocr_text)},
        ]

        encoded = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        )
        if isinstance(encoded, torch.Tensor):
            input_ids = encoded
        else:
            input_ids = encoded["input_ids"]

        target_device = next(self.model.parameters()).device
        input_ids = input_ids.to(target_device)

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=torch.ones_like(input_ids),
                max_new_tokens=2048,
                do_sample=False,
                temperature=1.0,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        raw = self.tokenizer.decode(
            outputs[0][input_ids.shape[1]:], skip_special_tokens=True
        ).strip()

        return _parse_json(raw)


def _parse_json(raw: str) -> Optional[dict]:
    """LLM 출력에서 JSON 추출. 마크다운 코드블록 처리 포함."""
    # ```json ... ``` 제거
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if match:
        raw = match.group(1).strip()

    # 첫 번째 { ~ 마지막 } 추출
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return None

    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return None


def dict_to_passage_item(data: dict, item_id: str, page: int) -> PassageItem:
    """파싱된 dict → PassageItem 변환."""
    questions = []
    for q in data.get("questions", []):
        questions.append(Question(
            number=q.get("number", 0),
            stem=q.get("stem", ""),
            options=q.get("options", []),
            answer=q.get("answer"),
            commentary=q.get("commentary"),
        ))

    return PassageItem(
        id=item_id,
        source_page=page,
        genre=data.get("genre"),
        passage=data.get("passage"),
        questions=questions,
    )
