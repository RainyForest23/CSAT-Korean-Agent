"""
Question Analyzer: 문제 분석

- 문제 유형 분류 (일치불일치 / 추론 / 빈칸 / 순서 / 서술형)
- 각 선지별 정오 판단 근거 추출
- 출제 포인트 파악
"""


class QuestionAnalyzer:
    def run(self, state):
        raise NotImplementedError
