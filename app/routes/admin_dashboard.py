from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.ram import RAM
from app.models.os import OS
from app.models.game import Game
from app.models.activity import Activity
from app.authentication.admin_jwt import get_current_admin

router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return {
        "total_games": db.query(Game).count(),
        "total_cpus": db.query(CPU).count(),
        "total_gpus": db.query(GPU).count(),
        "total_rams": db.query(RAM).count(),
        "total_oses": db.query(OS).count(),
    }


@router.get("/activity")
def get_recent_activity(db: Session = Depends(get_db)):
    """Get recent activity from the activities table"""
    activities = db.query(Activity).order_by(Activity.timestamp.desc()).limit(20).all()
    
    return {"activity": [activity.to_dict() for activity in activities]}