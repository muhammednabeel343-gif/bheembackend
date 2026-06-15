from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User
from app.models.game import Game
from app.services.community_service import CommunityService
from app.schemas.community import (
    CommunityPostResponse,
    CreatePostRequest,
    AddReactionRequest,
    RemoveReactionRequest,
    AddCommentRequest,
    CommunityFeedResponse,
    CommentResponse,
    PostReactionResponse
)

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/feed", response_model=CommunityFeedResponse)
async def get_feed(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get community feed (newest posts first)."""
    posts = CommunityService.get_community_feed(db, limit=limit, offset=offset)
    
    responses = []
    for post in posts:
        # Build reaction summary
        reactions = CommunityService.get_reactions(db, post.id)
        reactions_response = []
        for emoji, count in reactions.items():
            user_reacted = CommunityService.user_has_reacted(
                db, post.id, current_user.id, emoji
            )
            reactions_response.append(PostReactionResponse(
                emoji=emoji,
                count=count,
                user_reacted=user_reacted
            ))
        
        # Build comments
        comments = CommunityService.get_comments(db, post.id)
        comments_response = []
        for comment in comments:
            comments_response.append(CommentResponse(
                id=comment.id,
                user_id=comment.user_id,
                username=comment.user.username,
                comment=comment.comment,
                created_at=comment.created_at
            ))
        
        # Get game details if attached
        game_name = None
        game_image_url = None
        if post.game_id:
            game = db.query(Game).filter(Game.id == post.game_id).first()
            if game:
                game_name = game.name
                game_image_url = game.image_url
        
        responses.append(CommunityPostResponse(
            id=post.id,
            user_id=post.user_id,
            username=post.user.username,
            content=post.content,
            game_id=post.game_id,
            game_name=game_name,
            game_image_url=game_image_url,
            created_at=post.created_at,
            reactions=reactions_response,
            comments=comments_response,
            comment_count=len(comments_response)
        ))
    
    return CommunityFeedResponse(
        posts=responses,
        total_count=len(responses)
    )


@router.post("/posts", response_model=CommunityPostResponse)
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new community post."""
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty")
    
    # Verify game exists if provided
    if request.game_id:
        game = db.query(Game).filter(Game.id == request.game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
    
    post = CommunityService.create_post(
        db,
        current_user.id,
        request.content,
        request.game_id
    )
    
    # Get game details if attached
    game_name = None
    game_image_url = None
    if post.game_id:
        game = db.query(Game).filter(Game.id == post.game_id).first()
        if game:
            game_name = game.name
            game_image_url = game.image_url
    
    return CommunityPostResponse(
        id=post.id,
        user_id=post.user_id,
        username=post.user.username,
        content=post.content,
        game_id=post.game_id,
        game_name=game_name,
        game_image_url=game_image_url,
        created_at=post.created_at,
        reactions=[],
        comments=[],
        comment_count=0
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only author can delete)."""
    success = CommunityService.delete_post(db, post_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")
    return {"message": "Post deleted"}


@router.post("/posts/{post_id}/reactions")
async def add_reaction(
    post_id: int,
    request: AddReactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an emoji reaction to a post."""
    post = CommunityService.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    CommunityService.add_reaction(db, post_id, current_user.id, request.emoji)
    return {"message": "Reaction added"}


@router.delete("/posts/{post_id}/reactions/{emoji}")
async def remove_reaction(
    post_id: int,
    emoji: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an emoji reaction from a post."""
    post = CommunityService.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    success = CommunityService.remove_reaction(db, post_id, current_user.id, emoji)
    if not success:
        raise HTTPException(status_code=404, detail="Reaction not found")
    return {"message": "Reaction removed"}


@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: int,
    request: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post."""
    post = CommunityService.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not request.comment.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    
    comment = CommunityService.add_comment(db, post_id, current_user.id, request.comment)
    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        username=current_user.username,
        comment=comment.comment,
        created_at=comment.created_at
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only author can delete)."""
    success = CommunityService.delete_comment(db, comment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    return {"message": "Comment deleted"}


@router.get("/games/list")
async def get_games_for_attachment(
    search: Optional[str] = Query(None),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of games for post attachment."""
    query = db.query(Game)
    
    if search:
        query = query.filter(Game.name.ilike(f"%{search}%"))
    
    games = query.limit(limit).all()
    
    return {
        "games": [
            {
                "id": game.id,
                "name": game.name,
                "image_url": game.image_url
            }
            for game in games
        ]
    }
