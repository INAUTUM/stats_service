from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from celery.result import AsyncResult  # type: ignore
from sqlalchemy import select

from app.database import get_db, engine
from app import models, schemas, tasks
from app.schemas import DeviceOut, DeviceCreate, UserCreate, StatCreate, TaskStatus, UserOut, StatResponse

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/users/", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    return result.scalars().all()

@app.post("/users/", response_model=UserOut)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка уникальности email
    existing_user = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = models.User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/devices/", response_model=DeviceOut)
async def create_device(
    device: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка существования пользователя
    user = await db.get(models.User, device.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_device = models.Device(user_id=device.user_id)
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device

@app.post("/devices/{device_id}/stats/")
async def add_stat(
    device_id: UUID,
    stat: StatCreate,
    db: AsyncSession = Depends(get_db)
):
    device = await db.get(models.Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db_stat = models.Stat(**stat.dict(), device_id=device_id)
    db.add(db_stat)
    await db.commit()
    await db.refresh(db_stat)  # Важное обновление!
    return {"status": "ok"}

@app.get("/devices/{device_id}", response_model=schemas.DeviceOut)
async def get_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    device = await db.get(models.Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.get("/devices/{device_id}/analytics/", response_model=schemas.TaskStatus)
async def get_device_analytics(
    device_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None
):
    task = tasks.analyze_device_stats.delay(
        str(device_id),
        start.isoformat() if start else None,
        end.isoformat() if end else None
    )
    return {
        "task_id": task.id,
        "status": "PENDING",
        "result": None
    }

@app.get("/tasks/{task_id}", response_model=schemas.TaskStatus)
async def get_task_result(task_id: str):
    task = AsyncResult(task_id, app=tasks.celery)
    
    if task.ready():
        result = task.result
        return {
            "task_id": task_id,
            "status": result.get("status", "UNKNOWN"),
            "result": result.get("result"),
            "error": result.get("error")
        }
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": None
    }

@app.get("/stats/", response_model=list[schemas.StatResponse])
async def get_all_stats(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Stat))
    stats = result.scalars().all()
    return stats

@app.get("/stats/{device_id}/", response_model=list[schemas.StatResponse])
async def get_device_stats(
    device_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    # Проверка существования устройства
    device = await db.get(models.Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Получение статистики для устройства
    result = await db.execute(
        select(models.Stat)
        .where(models.Stat.device_id == device_id)
        .order_by(models.Stat.timestamp.desc())
    )
    return result.scalars().all()