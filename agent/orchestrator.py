"""
Orchestrator: Agent 흐름 제어

Reader → RAG Retriever → Question Analyzer → Generator → Reflection
Reflection이 불충분하다고 판단하면 RAG Retriever로 돌아가 재검색.
"""
from dataclasses import dataclass, field
from typing import Optional

from agent.reader import ReaderAgent
from agent.retriever import RAGRetriever
from agent.analyzer import QuestionAnalyzer
from agent.generator import CommentaryGenerator
from agent.reflection import ReflectionAgent


@dataclass
class AgentState:
    passage: str
    question: str
    genre: Optional[str] = None
    passage_structure: Optional[dict] = None
    retrieved_refs: list = field(default_factory=list)
    question_analysis: Optional[dict] = None
    commentary: Optional[str] = None
    reflection: Optional[dict] = None
    iteration: int = 0


class KoreanAgentOrchestrator:
    MAX_ITERATIONS = 2

    def __init__(self):
        self.reader = ReaderAgent()
        self.retriever = RAGRetriever()
        self.analyzer = QuestionAnalyzer()
        self.generator = CommentaryGenerator()
        self.reflector = ReflectionAgent()

    def run(self, passage: str, question: str) -> str:
        state = AgentState(passage=passage, question=question)

        while state.iteration <= self.MAX_ITERATIONS:
            state = self.reader.run(state)
            state = self.retriever.run(state)
            state = self.analyzer.run(state)
            state = self.generator.run(state)
            state = self.reflector.run(state)

            if state.reflection.get("passed"):
                break

            state.iteration += 1

        return state.commentary
