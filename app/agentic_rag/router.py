from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agentic_rag.schemas import AgentAnswer, AgentQuestion
from app.agentic_rag.service import ask_agent
from app.database import get_db
from app.logger import get_logger

router = APIRouter(prefix="/api/agent", tags=["Agentic RAG"])
logger = get_logger(__name__)


@router.post("/ask", response_model=AgentAnswer, summary="Ask the shopping/backend assistant")
def ask_question(payload: AgentQuestion, db: Session = Depends(get_db)) -> AgentAnswer:
    """Plan retrieval tools, retrieve relevant context, and answer with source excerpts."""
    result = ask_agent(db, payload.question.strip())
    logger.info("Agentic RAG request completed; tools=%s", ",".join(result["tools_used"]))
    return AgentAnswer(**result)


@router.get("/health", tags=["Agentic RAG"], summary="Check the local RAG knowledge base")
def agent_health() -> dict[str, str | int]:
    from app.agentic_rag.service import _load_knowledge

    records = _load_knowledge()
    return {"status": "ok", "service": "agentic-rag", "knowledge_documents": len(records)}
