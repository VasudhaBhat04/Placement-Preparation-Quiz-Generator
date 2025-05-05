import os
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()


class AptitudeQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class LogicalReasoningQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class TechnicalQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuestionGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv('GROQ_API_KEY'),
            model="llama-3.1-8b-instant",
            temperature=0.9
        )
        self.technical_topics = [
            "OOPs", "DBMS", "Computer Networks", "AI", "ML", "Data Structures", "Algorithms",
            "Time Complexity", "Object-Oriented Programming", "Dynamic Programming", "Recursion", 
            "Sorting Algorithms", "Searching Algorithms", "Graphs", "Stacks and Queues", "Trees", 
            "Hashing", "Database Management Systems", "Operating Systems", "Networking", "Concurrency", 
            "Software Engineering", "System Design"
        ]
        self.non_technical_topics = [
            "Aptitude", "Logical Reasoning", "Verbal Reasoning", "Puzzles", "Grammar", "English", "Percentage", 
            "Age Problems", "Time/Speed/Distance", "Series", "Seating Arrangements"
        ]

    def validate_topic(self, module, topic):
        if module == "Technical" and topic not in self.technical_topics:
            raise ValueError(f"Invalid technical topic. Choose from: {', '.join(self.technical_topics)}")
        elif module == "Non-Technical" and topic not in self.non_technical_topics:
            raise ValueError(f"Invalid non-technical topic. Choose from: {', '.join(self.non_technical_topics)}")

    def generate_question(self, module, topic, difficulty="medium"):
        self.validate_topic(module, topic)
        if module == "Technical":
            return self.generate_technical_question(topic, difficulty)
        elif module == "Non-Technical":
            return self.generate_non_technical_question(topic)

    def generate_technical_question(self, topic, difficulty="medium"):
        prompt = PromptTemplate(
            template=(
                "Generate a unique {difficulty} level technical question for {topic}.\n"
                "Respond in JSON only:\n"
                '{{\n'
                '    "question": "...",\n'
                '    "options": ["...", "...", "...", "..."],\n'
                '    "correct_answer": "...",\n'
                '    "explanation": "..." \n'
                '}}'
            ),
            input_variables=["topic", "difficulty"]
        )
        return self._generate_question(prompt, TechnicalQuestion, topic, difficulty)

    def generate_non_technical_question(self, topic):
        prompt = PromptTemplate(
            template=(
                "Generate a unique non-technical question for {topic}.\n"
                "Respond in JSON only:\n"
                '{{\n'
                '    "question": "...",\n'
                '    "options": ["...", "...", "...", "..."],\n'
                '    "correct_answer": "...",\n'
                '    "explanation": "..." \n'
                '}}'
            ),
            input_variables=["topic"]
        )
        return self._generate_question(prompt, AptitudeQuestion if "Aptitude" in topic else LogicalReasoningQuestion, topic)

    def _generate_question(self, prompt, pydantic_object, topic, difficulty=None):
        formatted = prompt.format(topic=topic, difficulty=difficulty) if difficulty else prompt.format(topic=topic)
        response = self.llm.invoke(formatted)
        try:
            return pydantic_object.parse_raw(response.content)
        except Exception as e:
            print("Parsing failed:", response.content)
            raise e