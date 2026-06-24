from typing import List, Optional
from pydantic import BaseModel, Field


class TaskItem(BaseModel):
    type: str
    question: str
    options: Optional[List[str]] = None
    answer_space: bool = True
    answer: Optional[str] = None


class PackPage(BaseModel):
    page_number: int
    page_type: str
    title: str
    instruction: str
    tasks: List[TaskItem] = []


class AnswerBlock(BaseModel):
    page_number: int
    answers: List[str]


class StudyPack(BaseModel):
    title: str
    subtitle: str
    language: str
    age: int
    grade: str
    topic: str
    pack_type: str
    difficulty: str
    parent_instruction: Optional[str] = ""
    pages: List[PackPage]
    answers: List[AnswerBlock] = []


class PackRequest(BaseModel):
    age: int = Field(ge=4, le=10)
    grade: str
    language: str
    pack_type: str
    topic: str
    pages_count: int = Field(ge=8, le=40)
    difficulty: str
    include_answers: bool = True
    include_parent_instruction: bool = True
    style: str = "print_bw"
    child_name: Optional[str] = ""
    output_dir: str = "output"
