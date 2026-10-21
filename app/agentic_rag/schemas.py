from pydantic import BaseModel, Field


class AgentQuestion(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="Question about the shop catalog or this backend")


class AgentSource(BaseModel):
    source: str
    title: str
    excerpt: str


class AgentAnswer(BaseModel):
    question: str
    answer: str
    tools_used: list[str]
    answer_mode: str
    sources: list[AgentSource]
