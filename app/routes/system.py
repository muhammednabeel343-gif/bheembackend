import platform
import subprocess
from app.schemas.compatibility import SimulatorRequest
from app.services.compatibility_service import (
    compute_compatibility_report,
    get_all_cpus,
    get_all_gpus,
    get_all_rams,
    get_all_storages,
)
from app.models.game import Game
from app.models.user_scan import UserScan

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.compatibility import (
    SystemScanResponse,
    SaveSystemScanRequest,
)
from app.services.compatibility_service import save_system_scan
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User

import psutil
import cpuinfo

router = APIRouter(prefix="/system", tags=["system"])

def get_gpu_name():
    try:
        result = subprocess.run(
            [
                "wmic",
                "path",
                "win32_VideoController",
                "get",
                "name",
            ],
            capture_output=True,
            text=True,
        )

        gpus = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and line.strip() != "Name"
        ]

        for gpu in gpus:
            if "NVIDIA" in gpu.upper():
                return gpu

        for gpu in gpus:
            if "AMD" in gpu.upper() or "RADEON" in gpu.upper():
                return gpu

        if gpus:
            return gpus[0]

    except Exception as e:
        print("GPU DETECTION ERROR:", e)

    return "Unknown GPU"


def get_real_system_specs():
    try:
        cpu = cpuinfo.get_cpu_info().get("brand_raw", "Unknown CPU")
    except Exception as e:
        print("CPU DETECTION ERROR:", e)
        cpu = "Unknown CPU"

    try:
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    except Exception:
        ram_gb = 0

    try:
        storage_gb = round(psutil.disk_usage("C:\\").total / (1024 ** 3))
    except Exception:
        storage_gb = 0

    try:
        gpu_name = get_gpu_name()
    except Exception as e:
        print("GPU DETECTION ERROR:", e)
        gpu_name = "Unknown GPU"

    return {
        "cpu": cpu,
        "gpu": gpu_name,
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "operating_system": platform.system(),
    }


@router.get("/scan", response_model=SystemScanResponse)
async def scan_system(
    current_user: User = Depends(get_current_user),
):
    specs = get_real_system_specs()

    print("REAL SYSTEM SCAN:", specs)

    return SystemScanResponse(
        cpu=specs["cpu"],
        gpu=specs["gpu"],
        ram_gb=specs["ram_gb"],
        storage_gb=specs["storage_gb"],
        operating_system=specs["operating_system"],
    )


@router.post("/save-scan")
async def save_scan(
    payload: SaveSystemScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print("SAVE_SCAN HIT")
    print("PAYLOAD:", payload.model_dump())

    try:
        scan = save_system_scan(
            db,
            current_user.id,
            payload,
        )

        print("SCAN CREATED")

        return {
            "cpu": scan.cpu,
            "gpu": scan.gpu,
            "ram_gb": scan.ram_gb,
            "storage_gb": scan.storage_gb,
            "operating_system": scan.operating_system,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        print("SAVE_SCAN ERROR:", repr(e))
        raise


@router.get("/hardware/cpus")
async def get_cpus(db: Session = Depends(get_db)):
    cpus = get_all_cpus(db)
    return [{"name": cpu.name, "score": 0} for cpu in cpus]


@router.get("/hardware/gpus")
async def get_gpus(db: Session = Depends(get_db)):
    gpus = get_all_gpus(db)
    return [{"name": gpu.name, "score": 0} for gpu in gpus]


@router.get("/hardware/rams")
async def get_rams(db: Session = Depends(get_db)):
    rams = get_all_rams(db)
    return [{"size": ram.size, "value": ram.size, "label": f"{ram.size} GB"} for ram in rams]


@router.get("/hardware/storages")
async def get_storages(db: Session = Depends(get_db)):
    storages = get_all_storages(db)
    return [{"size": storage.size} for storage in storages]


@router.post("/simulate")
async def simulate_compatibility(
    payload: SimulatorRequest,
    db: Session = Depends(get_db),
):
    game = (
        db.query(Game)
        .filter(Game.id == payload.game_id)
        .first()
    )

    if not game:
        raise ValueError("Game not found")

    requirement = game.requirements[0] if game.requirements else None
    if not requirement:
        raise ValueError("Game requirements not found")

    fake_scan = UserScan(
        cpu=payload.cpu,
        gpu=payload.gpu,
        ram_gb=payload.ram_gb,
        storage_gb=payload.storage_gb,
        operating_system="Windows",
    )

    return compute_compatibility_report(
        requirement,
        fake_scan,
    )