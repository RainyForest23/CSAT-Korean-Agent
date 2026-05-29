# CSAT Korean Agent

강민철 강사의 국어 강의 방식을 학습한 수능 국어 해설 생성 Agent.

## 목표

- **Input**: 수능/모의고사 지문 + 문제
- **Output**: 강민철 스타일 단계별 해설

## 아키텍처

```
입력: 지문 + 문제
        │
   [Orchestrator]
        │
        ├─ 1. Reader Agent        지문 구조 분석, 장르 파악
        ├─ 2. RAG Retriever       강민철 해설 DB 검색
        ├─ 3. Question Analyzer   문제 유형 분류, 선지 분석
        ├─ 4. Generator           강민철 스타일 해설 생성
        └─ 5. Reflection Agent    자가 검증, 필요 시 재검색
        │
출력: 강민철 스타일 해설
```

## 디렉토리 구조

```
├── data/                   데이터 파이프라인 산출물
│   ├── raw/                스캔본 원본
│   ├── ocr/                OCR 결과
│   ├── structured/         구조화된 (지문, 문제, 해설) JSON
│   ├── matched/            기출 지문 매칭 완료
│   └── training/           학습용 최종 데이터셋
│
├── pipelines/              데이터 처리 파이프라인
│   ├── 01_ocr/             스캔본 OCR
│   ├── 02_structure/       OCR → (지문/문제/해설) 구조화
│   ├── 03_match/           기출 지문 DB 매칭
│   └── 04_qa/              데이터 품질 관리
│
├── agent/                  Agent 구현
│   ├── orchestrator.py     Agent 흐름 제어
│   ├── reader.py           Reader Agent
│   ├── retriever.py        RAG Retriever
│   ├── analyzer.py         Question Analyzer
│   ├── generator.py        Commentary Generator
│   ├── reflection.py       Reflection Agent
│   └── tools/              Agent 도구 (장르분류기 등)
│
├── prompts/                Prompt Harness
│   ├── reader.yaml
│   ├── analyzer.yaml
│   ├── generator.yaml
│   └── reflection.yaml
│
├── models/                 모델 학습
│   ├── finetune/           Fine-tuning 스크립트 (EXAONE)
│   └── dpo/                DPO (스타일 preference 학습)
│
├── evaluation/             평가 파이프라인
│   ├── metrics.py          자동 평가 지표
│   ├── benchmark.py        벤치마크 실행
│   └── human_eval/         인간 평가 인터페이스
│
├── vector_db/              강민철 해설 벡터 DB
├── experiments/            실험 추적 (MLflow/WandB)
└── serving/                서빙 인프라
```

## 데이터 파이프라인

```
data/pdf/          스캔본 PDF 원본 (gitignore)
    ↓ [01_parse]   opendataloader-pdf → Markdown 변환
data/markdown/     지식베이스 — 헤딩/표/리스트 구조 보존 (gitignore)
    ↓ [02_structure] EXAONE으로 (지문/문제/해설) 추출
data/structured/   학습용 JSON (gitignore)
    ↓ [03_match]   기출 지문 DB와 매칭
data/matched/      매칭 완료 데이터 (gitignore)
    ↓ [04_qa]      품질 검증
data/training/     최종 학습 데이터 (gitignore)
```

## 개발 단계

| Phase | 내용 | 상태 |
|-------|------|------|
| 1 | 데이터 파이프라인 (PDF → Markdown → 구조화 → 매칭) | 🔲 |
| 2 | 평가 파이프라인 설계 | 🔲 |
| 3 | RAG MVP (해설 검색 + 생성) | 🔲 |
| 4 | Prompt Harness 설계 | 🔲 |
| 5 | Fine-tuning (EXAONE) | 🔲 |
| 6 | DPO (스타일 preference 학습) | 🔲 |
| 7 | Agent 조립 | 🔲 |
| 8 | 서빙 | 🔲 |

## 기술 스택

- **Base 모델**: EXAONE-4.0.1-32B
- **Orchestration**: LangGraph
- **Vector DB**: FAISS
- **실험 추적**: MLflow
- **PDF 파싱**: opendataloader-pdf (벤치마크 1위, 스캔본 OCR 포함)
