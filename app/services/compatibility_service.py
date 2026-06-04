from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user_scan import UserScan
from app.models.game import Game
from app.models.requirement import Requirement
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.ram import RAM
from app.models.storage import Storage
from app.schemas.compatibility import SaveSystemScanRequest
from app.data.cpu_benchmarks import CPU_BENCHMARKS
from app.data.gpu_benchmarks import GPU_BENCHMARKS
from app.services.game_service import get_game_by_id

def get_all_cpus(db: Session) -> List[CPU]:
    return db.query(CPU).all()

def get_all_gpus(db: Session) -> List[GPU]:
    return db.query(GPU).all()

def get_all_rams(db: Session) -> List[RAM]:
    return db.query(RAM).all()

def get_all_storages(db: Session) -> List[Storage]:
    return db.query(Storage).all()

def save_system_scan(db: Session, user_id: int, payload: SaveSystemScanRequest) -> UserScan:
    if payload.game_id is not None:
        game = db.query(Game).filter(Game.id == payload.game_id).first()
        if not game:
            raise ValueError("Game not found")
    scan = UserScan(
        user_id=user_id,
        game_id=payload.game_id,
        cpu=payload.cpu,
        gpu=payload.gpu,
        ram_gb=payload.ram_gb,
        storage_gb=payload.storage_gb,
        operating_system=payload.operating_system,
        compatibility_score=0.0,
        fps_estimate=0,
        status="Pending",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_latest_user_scan(db: Session, user_id: int) -> Optional[UserScan]:
    return (
        db.query(UserScan)
        .filter(UserScan.user_id == user_id)
        .order_by(UserScan.scan_time.desc())
        .first()
    )




def get_cpu_score(cpu_name: str) -> int:
    cpu_name = (cpu_name or "").lower()

    for cpu, score in CPU_BENCHMARKS.items():
        if cpu in cpu_name:
            return score

    return 40


def get_gpu_score(gpu_name: str) -> int:
    gpu_name = (gpu_name or "").lower()

    for gpu, score in GPU_BENCHMARKS.items():
        if gpu in gpu_name:
            return score

    return 20



def compute_compatibility_report(requirement: Requirement, scan: UserScan) -> dict:
    
    required_cpu_score = get_cpu_score(requirement.cpu)
    user_cpu_score = get_cpu_score(scan.cpu)

    required_gpu_score = get_gpu_score(requirement.gpu)
    user_gpu_score = get_gpu_score(scan.gpu)

    cpu_ratio = min(
        user_cpu_score / max(required_cpu_score, 1),
        1.0
    )

    gpu_ratio = min(
        user_gpu_score / max(required_gpu_score, 1),
        1.0
    )

    ram_ratio = min(
        scan.ram_gb / max(requirement.ram_gb or 1, 1),
        1.0
    )

    storage_ratio = min(
        scan.storage_gb / max(requirement.storage_gb or 1, 1),
        1.0
    )
    performance_score = (
        gpu_ratio * 0.60 +
        cpu_ratio * 0.25 +
        ram_ratio * 0.10 +
        storage_ratio * 0.05
    )
    cpu_pass = cpu_ratio >= 0.80
    gpu_pass = gpu_ratio >= 0.80
    ram_pass = ram_ratio >= 1.00
    storage_pass = storage_ratio >= 1.00

    cpu_score = cpu_ratio * 30
    gpu_score = gpu_ratio * 40
    ram_score = ram_ratio * 15
    storage_score = storage_ratio * 15

    total_score = round(
        cpu_score +
        gpu_score +
        ram_score +
        storage_score
    )

    if total_score >= 90:
        status = "Excellent"
    elif total_score >= 70:
        status = "Playable"
    elif total_score >= 50:
        status = "Limited"
    else:
        status = "Not Recommended"

    base_fps = int(performance_score * 140)

    estimated_fps = {
        "low": max(20, base_fps),
        "medium": max(15, int(base_fps * 0.75)),
        "high": max(10, int(base_fps * 0.55)),
        "ultra": max(5, int(base_fps * 0.40)),
    }
    return {
        "minimum_requirements": {
            "cpu": requirement.cpu,
            "gpu": requirement.gpu,
            "ram_gb": requirement.ram_gb,
            "storage_gb": requirement.storage_gb,
            "directx": requirement.directx,
            "operating_system": requirement.operating_system
        },
        "user_specs": {
            "cpu": scan.cpu,
            "gpu": scan.gpu,
            "ram_gb": scan.ram_gb,
            "storage_gb": scan.storage_gb,
            "operating_system": scan.operating_system,
        },
        "checks": {
            "cpu_pass": cpu_pass,
            "gpu_pass": gpu_pass,
            "ram_pass": ram_pass,
            "storage_pass": storage_pass,
        },
        "compatibility_percentage": total_score,
        "status": status,
        "estimated_fps": estimated_fps,
    }


def create_game_compatibility_record(db: Session, user_id: int, game: Game, scan: UserScan, report: dict) -> UserScan:
    compatibility_scan = UserScan(
        user_id=user_id,
        game_id=game.id,
        cpu=scan.cpu,
        gpu=scan.gpu,
        ram_gb=scan.ram_gb,
        storage_gb=scan.storage_gb,
        operating_system=scan.operating_system,
        compatibility_score=report["compatibility_percentage"],
        fps_estimate=report["estimated_fps"]["medium"],
        status=report["status"],
    )
    db.add(compatibility_scan)
    db.commit()
    db.refresh(compatibility_scan)
    return compatibility_scan


def build_game_compatibility(db: Session, user_id: int, game_id: int) -> dict:
    game = get_game_by_id(db, game_id)
    if not game:
        raise ValueError("Game not found")

    scan = get_latest_user_scan(db, user_id)
    if not scan:
        raise ValueError("No system scan available")

    requirement = game.requirements[0] if game.requirements else None
    if not requirement:
        raise ValueError("Game requirements not found")

    report = compute_compatibility_report(requirement, scan)
    create_game_compatibility_record(db, user_id, game, scan, report)
    return report
