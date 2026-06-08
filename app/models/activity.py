from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Activity type: 'game', 'cpu', 'gpu', 'ram', 'storage'
    entity_type = Column(String(50), nullable=False, index=True)
    
    # Entity ID (game_id, cpu_id, etc.)
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Entity name/title for display
    entity_name = Column(String(255), nullable=False)
    
    # Action: 'created', 'updated', 'deleted'
    action = Column(String(50), nullable=False, index=True)
    
    # Description of what changed
    description = Column(String(500), nullable=True)
    
    # Timestamp of activity
    timestamp = Column(DateTime(timezone=False), server_default=func.now(), index=True)

    def to_dict(self):
        """Convert to dictionary for API response"""
        action_labels = {
            'created': 'added',
            'updated': 'updated',
            'deleted': 'deleted'
        }
        
        icon_map = {
            'game': 'Gamepad2',
            'cpu': 'Cpu',
            'gpu': 'Gpu',
            'ram': 'HardDrive',
            'storage': 'HardDrive',
        }
        
        action_label = action_labels.get(self.action, self.action)
        
        return {
            "id": f"{self.entity_type}-{self.id}",
            "type": self.entity_type,
            "title": f"{self.entity_name} {action_label}",
            "description": self.description or f"{self.entity_type.capitalize()} {action_label}",
            "timestamp": self.timestamp,
            "icon_type": icon_map.get(self.entity_type, 'Activity'),
            "action": self.action,
        }
