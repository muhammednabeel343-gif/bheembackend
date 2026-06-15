from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.authentication.jwt import get_current_user
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/ai", tags=["AI"])


class ChatRequest(BaseModel):
    message: str


class ChatResponseMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    conversation: List[ChatResponseMessage]


class ResetResponse(BaseModel):
    success: bool
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        service = ChatbotService(db, current_user)
        result = service.ask(request.message)
        return {
            "answer": result["answer"],
            "conversation": [
                ChatResponseMessage(role=msg["role"], content=msg["content"])
                for msg in result["conversation"]
            ],
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat/reset", response_model=ResetResponse)
async def reset_chat(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ChatbotService(db, current_user)
    service.reset_history()
    return {"success": True, "message": "Chat history cleared."}
