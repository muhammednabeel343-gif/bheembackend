import platform
import subprocess
from app.schemas.compatibility import SimulatorRequest
from app.services.compatibility_service import (
    compute_compatibility_report,
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
from app.services.compatibility_service import (
    CPU_BENCHMARKS,
    GPU_BENCHMARKS,
)

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

        # Prefer NVIDIA
        for gpu in gpus:
            if "NVIDIA" in gpu.upper():
                return gpu

        # Then AMD
        for gpu in gpus:
            if "AMD" in gpu.upper() or "RADEON" in gpu.upper():
                return gpu

        # Otherwise use first available GPU
        if gpus:
            return gpus[0]

    except Exception as e:
        print("GPU DETECTION ERROR:", e)

    return "Unknown GPU"


def get_real_system_specs():
    cpu = cpuinfo.get_cpu_info().get(
        "brand_raw",
        "Unknown CPU"
    )

    ram_gb = round(
        psutil.virtual_memory().total / (1024 ** 3)
    )

    storage_gb = round(
        psutil.disk_usage("C:\\").total / (1024 ** 3)
    )

    gpu_name = get_gpu_name()

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
async def get_cpus():
    return [
        {
            "name": cpu,
            "score": score,
        }
        for cpu, score in CPU_BENCHMARKS.items()
    ]


@router.get("/hardware/gpus")
async def get_gpus():
    return [
        {
            "name": gpu,
            "score": score,
        }
        for gpu, score in GPU_BENCHMARKS.items()
    ]
    
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

    requirement = game.requirements[0]

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