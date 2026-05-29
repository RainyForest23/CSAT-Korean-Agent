# 01_parse: 교재 PDF → Markdown 지식베이스

opendataloader-pdf 기반으로 스캔본 포함 PDF를 Markdown으로 변환.
변환된 Markdown은 `data/markdown/`에 지식베이스로 저장되어
RAG 인덱싱 및 02_structure 구조화의 입력으로 사용.

## 사전 요구사항

```bash
# Java 11+ 확인
java -version

# 없으면 설치: https://adoptium.net/

# Python 패키지
pip install opendataloader-pdf
```

## 사용법

```bash
# data/pdf/ 전체 변환 (기본)
python run_parse.py

# 이어서 처리 (완료된 파일 건너뜀)
python run_parse.py --resume

# 단일 파일
python run_parse.py ../../data/pdf/강민철_문학.pdf

# 출력 경로 지정
python run_parse.py --output ../../data/markdown/
```

## 출력 구조

```
data/markdown/
├── 강민철_문학/
│   ├── 강민철_문학.md      ← 지식베이스 (RAG 청킹 대상)
│   └── 강민철_문학.json    ← bbox 정보 (좌표 기반 검색용)
├── 강민철_독서/
│   ├── 강민철_독서.md
│   └── 강민철_독서.json
```

## Markdown이 지식베이스인 이유

| 항목 | raw OCR | Markdown (opendataloader-pdf) |
|------|---------|-------------------------------|
| 읽기 순서 | 무너짐 | XY-Cut++ 알고리즘으로 보존 |
| 구조 | 없음 | 헤딩/리스트/표 보존 |
| 사람이 수정 | 어려움 | 가능 |
| RAG 청킹 | 임의 분할 | 헤딩 기준 자연스러운 분할 |
| 정확도 | 낮음 | 벤치마크 1위 (0.907) |

## 파이프라인 위치

```
data/pdf/          (스캔본 원본, gitignore)
    ↓ [01_parse]
data/markdown/     (지식베이스, gitignore)
    ↓ [02_structure]
data/structured/   (학습용 JSON, gitignore)
```
