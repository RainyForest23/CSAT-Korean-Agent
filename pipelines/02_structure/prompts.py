"""
구조화 LLM 프롬프트

교재 OCR 텍스트에서 (지문/문제/선지/정답/해설)을 추출하는 프롬프트.
"""

SYSTEM_PROMPT = """당신은 수능 국어 교재를 구조화하는 전문가입니다.
Markdown으로 변환된 교재 텍스트를 분석하여 정해진 JSON 형식으로 변환하세요.

Markdown 교재의 특징:
- 헤딩(#, ##)이 단원/섹션 구분에 사용됨
- 지문 앞에는 "다음 글을 읽고 물음에 답하시오" 형식
- 문제 번호는 숫자(1, 2, 3...) 또는 괄호 형식
- 선지는 ①②③④⑤ 형식
- 해설은 "해설", "풀이", "정답과 해설" 구분자 이후
- 장르: 현대시 / 현대소설 / 고전시가 / 고전소설 / 독서(비문학)

반드시 아래 JSON 형식으로만 출력하세요. 다른 텍스트 없이."""

EXTRACTION_TEMPLATE = """다음은 수능 국어 교재의 Markdown 텍스트입니다. 구조화하세요.

[Markdown 텍스트]
{markdown_text}

[출력 형식]
{{
  "genre": "현대시|현대소설|고전시가|고전소설|독서",
  "passage": "지문 전문 (없으면 null)",
  "questions": [
    {{
      "number": 1,
      "stem": "문제 본문",
      "options": ["①선지1", "②선지2", "③선지3", "④선지4", "⑤선지5"],
      "answer": "정답 번호 (없으면 null)",
      "commentary": "해설 전문 (없으면 null)"
    }}
  ]
}}"""


def build_prompt(markdown_text: str) -> str:
    return EXTRACTION_TEMPLATE.format(markdown_text=markdown_text[:4000])
