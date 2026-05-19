# 02_structure: OCR → 구조화 파이프라인

OCR JSON을 (지문, 문제, 선지, 정답, 해설) 단위로 구조화.
서버의 EXAONE 32B를 LLM으로 사용.

## 사용법

```bash
# 단일 파일 테스트 (처음 10페이지만)
python run_structure.py ../../data/ocr/강민철_문학_ocr.json --sample 10

# 전체 처리
python run_structure.py ../../data/ocr/강민철_문학_ocr.json --output ../../data/structured/

# 디렉토리 일괄 처리 + 이어하기
python run_structure.py ../../data/ocr/ --output ../../data/structured/ --resume

# 로컬 모델 경로 지정 (서버)
python run_structure.py ../../data/ocr/ --model /path/to/exaone
```

## 출력 형식

`data/structured/{파일명}_structured.json`

```json
{
  "source_ocr": "data/ocr/강민철_문학_ocr.json",
  "items": [
    {
      "id": "강민철_문학_0001",
      "source_page": 12,
      "genre": "현대시",
      "passage": "산은 날마다...",
      "questions": [
        {
          "number": 1,
          "stem": "윗글에 대한 설명으로 적절한 것은?",
          "options": ["①...", "②...", "③...", "④...", "⑤..."],
          "answer": "②",
          "commentary": "이 문제의 포인트는..."
        }
      ]
    }
  ]
}
```

## 파이프라인 흐름

```
data/ocr/*.json
  → run_structure.py
      → _group_pages()       3페이지씩 묶기 (지문+문제+해설 커버)
      → extractor.py         EXAONE으로 구조화
      → validate.py          QA 검증
  → data/structured/*.json
```

## 주의사항

- EXAONE 32B 로딩에 시간이 걸림 (최초 1회)
- 페이지 묶음 크기(`window=3`)는 교재에 따라 조정 필요
- QA 통과율 90% 미만이면 `--sample`로 프롬프트 점검 권장

## 다음 단계

구조화 완료 → `03_match/`에서 기출 지문 DB와 매칭
