"""
chat.py — REST routes for the new persistent, per-user chat system.

Prefix: /api/chat
Auth:   Bearer JWT (user only; admins are blocked)
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.authentication.jwt import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"


class RenameSessionRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    ai_available: bool


# ---------------------------------------------------------------------------
# Session endpoints
# ---------------------------------------------------------------------------

@router.get("/sessions", response_model=List[SessionOut])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all chat sessions for the current user, newest first."""
    svc = ChatService(db, current_user)
    return svc.list_sessions()


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new empty chat session."""
    svc = ChatService(db, current_user)
    return svc.create_session(title=body.title or "New Chat")


@router.patch("/sessions/{session_id}", response_model=SessionOut)
async def rename_session(
    session_id: int,
    body: RenameSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ChatService(db, current_user)
    session = svc.rename_session(session_id, body.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ChatService(db, current_user)
    if not svc.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")


# ---------------------------------------------------------------------------
# Message endpoints
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/messages", response_model=List[MessageOut])
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all messages in the given session."""
    svc = ChatService(db, current_user)
    session = svc.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return svc.get_messages(session_id)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: int,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message and receive the AI reply."""
    svc = ChatService(db, current_user)
    try:
        result = svc.send_message(session_id, body.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return SendMessageResponse(
        user_message=MessageOut.model_validate(result["user_message"]),
        assistant_message=MessageOut.model_validate(result["assistant_message"]),
        ai_available=result["ai_available"],
    )
