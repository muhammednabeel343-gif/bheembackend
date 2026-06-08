from app.schemas.ram import RAMCreate, RAMResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ram import RAM
from app.authentication.admin_jwt import get_current_admin
from app.utils.activity_logger import log_activity

router = APIRouter(
    prefix="/admin/rams",
    tags=["RAM Management"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[RAMResponse])
def get_rams(db: Session = Depends(get_db)):
    return db.query(RAM).all()


@router.get("/{ram_id}", response_model=RAMResponse)
def get_ram(ram_id: int, db: Session = Depends(get_db)):
    ram = db.query(RAM).filter(RAM.id == ram_id).first()
    if not ram:
        raise HTTPException(status_code=404, detail="RAM not found")
    return ram


@router.post("", response_model=RAMResponse)
def create_ram(
    ram: RAMCreate,
    db: Session = Depends(get_db)
):
    existing_ram = (
        db.query(RAM)
        .filter(RAM.size == ram.size)
        .first()
    )

    if existing_ram:
        raise HTTPException(
            status_code=400,
            detail="RAM size already exists"
        )

    new_ram = RAM(size=ram.size)
    db.add(new_ram)
    db.commit()
    db.refresh(new_ram)

    # Log activity
    log_activity(
        db,
        entity_type="ram",
        entity_id=new_ram.id,
        entity_name=f"{new_ram.size}GB",
        action="created",
        description=f"RAM {new_ram.size}GB added to hardware library"
    )

    return new_ram


@router.put("/{ram_id}", response_model=RAMResponse)
def update_ram(
    ram_id: int,
    ram: RAMCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(RAM).filter(RAM.id == ram_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="RAM not found")

    duplicate = db.query(RAM).filter(RAM.size == ram.size, RAM.id != ram_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="RAM size already exists")

    existing.size = ram.size
    db.commit()
    db.refresh(existing)

    # Log activity
    log_activity(
        db,
        entity_type="ram",
        entity_id=existing.id,
        entity_name=f"{existing.size}GB",
        action="updated",
        description=f"RAM {existing.size}GB updated"
    )

    return existing


@router.delete("/{ram_id}")
def delete_ram(ram_id: int, db: Session = Depends(get_db)):
    ram = db.query(RAM).filter(RAM.id == ram_id).first()
    if not ram:
        raise HTTPException(status_code=404, detail="RAM not found")
    
    ram_size = ram.size
    db.delete(ram)
    db.commit()

    # Log activity
    log_activity(
        db,
        entity_type="ram",
        entity_id=ram_id,
        entity_name=f"{ram_size}GB",
        action="deleted",
        description=f"RAM {ram_size}GB deleted"
    )

    return {"message": "RAM deleted"}