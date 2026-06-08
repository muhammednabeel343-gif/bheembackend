from sqlalchemy.orm import Session
from app.models.activity import Activity


def log_activity(
    db: Session,
    entity_type: str,
    entity_id: int,
    entity_name: str,
    action: str,
    description: str = None
) -> Activity:
    """
    Log an activity to the database.
    
    Args:
        db: Database session
        entity_type: Type of entity ('game', 'cpu', 'gpu', 'ram', 'storage')
        entity_id: ID of the entity
        entity_name: Name/title of the entity
        action: Action performed ('created', 'updated', 'deleted')
        description: Optional description of what changed
    
    Returns:
        The created Activity record
    """
    activity = Activity(
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        action=action,
        description=description,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
