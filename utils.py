import os
import re
import json
from typing import List, Optional, Set
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel

load_dotenv()


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


AptitudeQuestion = QuizQuestion
LogicalReasoningQuestion = QuizQuestion
TechnicalQuestion = QuizQuestion


class QuestionGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-8b-instant",
            temperature=0.95,
        )
        self.technical_topics = [
            "OOPs", "DBMS", "Computer Networks", "AI", "ML",
            "Data Structures", "Algorithms", "Time Complexity",
            "Dynamic Programming", "Recursion", "Sorting Algorithms",
            "Searching Algorithms", "Graphs", "Stacks and Queues",
            "Trees", "Hashing", "Operating Systems", "Networking",
            "Concurrency", "Software Engineering", "System Design",
        ]
        self.non_technical_topics = [
            "Aptitude", "Logical Reasoning", "Verbal Reasoning",
            "Puzzles", "Grammar", "English",
        ]

    def validate_topic(self, module: str, topic: str) -> None:
        pool = (
            self.technical_topics
            if module == "Technical"
            else self.non_technical_topics
        )
        if topic not in pool:
            raise ValueError(f"'{topic}' is not a valid {module} topic.")

    def generate_question(
        self,
        module: str,
        topic: str,
        difficulty: Optional[str] = "medium",
        seen_questions: Optional[Set[str]] = None,
    ) -> QuizQuestion:
        self.validate_topic(module, topic)
        if module == "Technical":
            return self._gen_technical(topic, difficulty or "medium", seen_questions)
        return self._gen_non_technical(topic, seen_questions)

    def _seen_block(self, seen: Optional[Set[str]]) -> str:
        if not seen:
            return ""
        recent = list(seen)[-10:]
        lines = "\n".join(f"  - {q}" for q in recent)
        return f"\nDo NOT reuse or paraphrase any of these already-asked questions:\n{lines}\n"

    def _json_schema(self) -> str:
        return (
            'Return ONLY a raw JSON object - no markdown, no code fences, no extra text:\n'
            '{"question":"...","options":["A. ...","B. ...","C. ...","D. ..."],'
            '"correct_answer":"A. ...","explanation":"..."}'
        )

    def _gen_technical(
        self, topic: str, difficulty: str, seen: Optional[Set[str]]
    ) -> QuizQuestion:
        prompt = (
            f"Generate a UNIQUE {difficulty}-level multiple-choice question on: {topic}.\n"
            f"{self._seen_block(seen)}"
            "Rules:\n"
            "  - The question must be different from every question listed above.\n"
            "  - Provide exactly 4 options labelled A, B, C, D.\n"
            "  - correct_answer must exactly match one of the option strings.\n\n"
            f"{self._json_schema()}"
        )
        return self._invoke_and_parse(prompt)

    def _gen_non_technical(self, topic: str, seen: Optional[Set[str]]) -> QuizQuestion:
        prompt = (
            f"Generate a UNIQUE multiple-choice question on: {topic}.\n"
            f"{self._seen_block(seen)}"
            "Rules:\n"
            "  - The question must be different from every question listed above.\n"
            "  - Provide exactly 4 options labelled A, B, C, D.\n"
            "  - correct_answer must exactly match one of the option strings.\n\n"
            f"{self._json_schema()}"
        )
        return self._invoke_and_parse(prompt)

    def _invoke_and_parse(self, prompt: str, retries: int = 3) -> QuizQuestion:
        last_err: Exception = RuntimeError("No attempts made")
        for attempt in range(retries):
            try:
                response = self.llm.invoke(prompt)
                raw = response.content.strip()

                raw = re.sub(r"```(?:json)?\s*", "", raw)
                raw = raw.replace("```", "").strip()

                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if not match:
                    raise ValueError("No JSON object found in LLM response.")
                json_str = match.group(0)

                data = json.loads(json_str)

                for key in ("question", "options", "correct_answer", "explanation"):
                    if key not in data:
                        raise KeyError(f"Missing key: '{key}'")

                if len(data["options"]) != 4:
                    raise ValueError("Expected exactly 4 options.")

                return QuizQuestion(**data)

            except Exception as exc:
                last_err = exc
                print(f"[QuestionGenerator] Attempt {attempt + 1}/{retries} failed: {exc}")

        raise RuntimeError(
            f"Failed to generate a valid question after {retries} attempts. "
            f"Last error: {last_err}"
        )
