# Commit Convention

```
<type>(<scope>): <subject>
```

## Type
| type | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `data` | 데이터 파이프라인 |
| `exp` | 실험 (fine-tuning, DPO, 평가) |
| `prompt` | 프롬프트 수정 |
| `refactor` | 리팩토링 |
| `docs` | 문서 |

## Scope
`ocr` / `structure` / `match` / `agent` / `eval` / `finetune` / `dpo` / `serving`

## 예시
```
data(ocr): Clova OCR 파이프라인 구현
exp(finetune): EXAONE LoRA 첫 학습 실행
prompt(generator): 강민철 스타일 few-shot 예시 추가
feat(agent): Reflection Agent 재검색 루프 구현
```
