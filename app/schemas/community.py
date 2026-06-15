from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class PostReactionResponse(BaseModel):
    emoji: str
    count: int
    user_reacted: bool = False

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: str
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunityPostResponse(BaseModel):
    id: int
    user_id: int
    username: str
    content: str
    game_id: Optional[int] = None
    game_name: Optional[str] = None
    game_image_url: Optional[str] = None
    created_at: datetime
    reactions: List[PostReactionResponse] = []
    comments: List[CommentResponse] = []
    comment_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CreatePostRequest(BaseModel):
    content: str
    game_id: Optional[int] = None


class AddReactionRequest(BaseModel):
    emoji: str  # ❤️, 🔥, 🎮, 😎, ⚔️


class RemoveReactionRequest(BaseModel):
    emoji: str


class AddCommentRequest(BaseModel):
    comment: str


class CommunityFeedResponse(BaseModel):
    posts: List[CommunityPostResponse]
    total_count: int

    model_config = ConfigDict(from_attributes=True)
