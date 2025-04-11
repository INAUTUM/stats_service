from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from typing import Optional

class StatResponse(BaseModel):
    id: int
    x: float
    y: float
    z: float
    timestamp: datetime
    device_id: UUID

    class Config:
        from_attributes = True

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str

class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    user_id: int

class DeviceOut(BaseModel):
    id: UUID
    user_id: int

    class Config:
        from_attributes = True

class StatCreate(BaseModel):
    x: float
    y: float
    z: float

class AnalyticsResult(BaseModel):
    min: float
    max: float
    sum: float
    median: float
    count: int

# class TaskStatus(BaseModel):
#     task_id: str
#     status: str
#     result: Optional[AnalyticsResult] = None

# class TaskStatus(BaseModel):
#     task_id: str
#     status: str
#     result: dict | None = None
#     error: str | None = None