"""
Reflection Agent: 생성된 해설 자가 검증

- "강민철답지 않은 표현" 체크
- 정답 근거 누락 여부 확인
- passed: True → 완료 / False → RAG 재검색 후 재생성
"""


class ReflectionAgent:
    def run(self, state):
        raise NotImplementedError
