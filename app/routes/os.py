from app.schemas.os import OSCreate, OSResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.os import OS
from app.authentication.admin_jwt import get_current_admin
from app.utils.activity_logger import log_activity

router = APIRouter(
    prefix="/admin/os",
    tags=["OS Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[OSResponse])
def get_oses(db: Session = Depends(get_db)):
    return db.query(OS).all()


@router.get("/{os_id}", response_model=OSResponse)
def get_os(os_id: int, db: Session = Depends(get_db)):
    os = db.query(OS).filter(OS.id == os_id).first()
    if not os:
        raise HTTPException(status_code=404, detail="OS not found")
    return os


@router.post("", response_model=OSResponse)
def create_os(
    os: OSCreate,
    db: Session = Depends(get_db)
):
    existing_os = (
        db.query(OS)
        .filter(OS.name.ilike(os.name))
        .first()
    )

    if existing_os:
        raise HTTPException(
            status_code=400,
            detail="OS name already exists"
        )

    new_os = OS(name=os.name)
    db.add(new_os)
    db.commit()
    db.refresh(new_os)

    # Log activity
    log_activity(
        db,
        entity_type="os",
        entity_id=new_os.id,
        entity_name=new_os.name,
        action="created",
        description=f"OS {new_os.name} added to hardware library"
    )

    return new_os


@router.put("/{os_id}", response_model=OSResponse)
def update_os(
    os_id: int,
    os: OSCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(OS).filter(OS.id == os_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="OS not found")

    duplicate = db.query(OS).filter(OS.name.ilike(os.name), OS.id != os_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="OS name already exists")

    existing.name = os.name
    db.commit()
    db.refresh(existing)

    # Log activity
    log_activity(
        db,
        entity_type="os",
        entity_id=existing.id,
        entity_name=existing.name,
        action="updated",
        description=f"OS {existing.name} updated"
    )

    return existing


@router.delete("/{os_id}")
def delete_os(os_id: int, db: Session = Depends(get_db)):
    os = db.query(OS).filter(OS.id == os_id).first()
    if not os:
        raise HTTPException(status_code=404, detail="OS not found")
    
    os_name = os.name
    db.delete(os)
    db.commit()

    # Log activity
    log_activity(
        db,
        entity_type="os",
        entity_id=os_id,
        entity_name=os_name,
        action="deleted",
        description=f"OS {os_name} deleted"
    )

    return {"message": "OS deleted"}
