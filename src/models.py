import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.sql.sqltypes import DateTime

from src.settings import Base
from src.schemas import TaskStatus
from src.utils import current_datetime


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String)
    timestamp = Column(DateTime, default=current_datetime)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    status = Column(ENUM(TaskStatus), default=TaskStatus.TODO)
