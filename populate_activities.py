from app.database import SessionLocal
from app.models.activity import Activity
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.ram import RAM
from app.models.game import Game
from sqlalchemy import text

db = SessionLocal()

# Clear existing activities first
db.query(Activity).delete()
db.commit()

print('Adding activities for existing items with ACTUAL timestamps...')

# Games
games = db.query(Game).order_by(Game.created_at).all()
for game in games:
    activity = Activity(
        entity_type='game',
        entity_id=game.id,
        entity_name=game.name,
        action='created',
        description=f'Game "{game.name}" added',
        timestamp=game.created_at  # Use actual creation time
    )
    db.add(activity)
    print(f'  ✓ Logged game: {game.name} ({game.created_at})')

db.commit()

# CPUs
cpus = db.query(CPU).order_by(CPU.created_at).all()
for cpu in cpus:
    activity = Activity(
        entity_type='cpu',
        entity_id=cpu.id,
        entity_name=cpu.name,
        action='created',
        description=f'CPU "{cpu.name}" added to hardware library',
        timestamp=cpu.created_at  # Use actual creation time
    )
    db.add(activity)
    print(f'  ✓ Logged CPU: {cpu.name} ({cpu.created_at})')

db.commit()

# GPUs
gpus = db.query(GPU).order_by(GPU.created_at).all()
for gpu in gpus:
    activity = Activity(
        entity_type='gpu',
        entity_id=gpu.id,
        entity_name=gpu.name,
        action='created',
        description=f'GPU "{gpu.name}" added to hardware library',
        timestamp=gpu.created_at  # Use actual creation time
    )
    db.add(activity)
    print(f'  ✓ Logged GPU: {gpu.name} ({gpu.created_at})')

db.commit()

# RAMs
rams = db.query(RAM).order_by(RAM.created_at).all()
for ram in rams:
    activity = Activity(
        entity_type='ram',
        entity_id=ram.id,
        entity_name=f'{ram.size}GB',
        action='created',
        description=f'RAM {ram.size}GB added to hardware library',
        timestamp=ram.created_at  # Use actual creation time
    )
    db.add(activity)
    print(f'  ✓ Logged RAM: {ram.size}GB ({ram.created_at})')

db.commit()

print('\nDone! All activities logged with ACTUAL timestamps from when items were created.')
db.close()

