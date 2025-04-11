from celery import Celery # type: ignore
from app import models
from app.database import SyncSessionLocal
import numpy as np
from datetime import datetime
from sqlalchemy import and_
from typing import Optional

celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task(bind=True)
def analyze_device_stats(
    self, 
    device_id: str, 
    start: Optional[str] = None, 
    end: Optional[str] = None
):
    try:
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else datetime.utcnow()
        
        with SyncSessionLocal() as session:
            # Проверка существования устройства
            device = session.query(models.Device).get(device_id)
            if not device:
                return {"status": "FAILURE", "error": "Device not found"}
            
            # Построение запроса с фильтрацией
            query = session.query(
                models.Stat.x, 
                models.Stat.y, 
                models.Stat.z
            ).filter(
                models.Stat.device_id == device_id
            )
            
            if start_dt:
                query = query.filter(models.Stat.timestamp >= start_dt)
            if end_dt:
                query = query.filter(models.Stat.timestamp <= end_dt)
            
            # Получаем сырые данные внутри сессии
            stats_data = query.all()

        # Вычисляем значения после закрытия сессии
        values = [x + y + z for x, y, z in stats_data] if stats_data else []
        
        return {
            "status": "SUCCESS",
            "result": {
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "sum": sum(values),
                "median": float(np.median(values)) if values else 0.0,
                "count": len(values)
            }
        }
    
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}