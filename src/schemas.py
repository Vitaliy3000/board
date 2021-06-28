import datetime
import enum
import typing as t
import uuid

from pydantic import BaseModel, validator

from src.settings import HOURLY_RATE
from src.utils import current_datetime


SECONDS_IN_HOUR = 3600


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskBase(BaseModel):
    pass


class TaskCreate(TaskBase):
    name: str


class TaskUpdate(TaskBase):
    status: TaskStatus


class Task(TaskCreate, TaskUpdate, TaskBase):
    id: uuid.UUID
    timestamp: datetime.datetime
    start_time: t.Optional[datetime.datetime]
    end_time: t.Optional[datetime.datetime]
    time_in_work: t.Optional[datetime.timedelta]
    price: t.Optional[float]

    @validator("time_in_work", pre=True, always=True)
    def calculate_time_in_work(cls, v, values):
        if values["start_time"] is not None:
            last_time = (
                current_datetime() if values["end_time"] is None else values["end_time"]
            )
            return last_time - values["start_time"]

    @validator("price", pre=True, always=True)
    def calculate_price(cls, v, values):
        if values["time_in_work"] is not None:
            return (
                HOURLY_RATE * values["time_in_work"].total_seconds() / SECONDS_IN_HOUR
            )

    class Config:
        orm_mode = True
