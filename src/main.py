from datetime import datetime
from src.utils import current_datetime
import typing as t
import uuid

from sqlalchemy.sql.functions import mode

from fastapi import Depends, FastAPI, HTTPException
from mangum import Mangum
from sqlalchemy.orm import Session

from src import models, schemas, settings, utils


app = FastAPI(title="board API")

models.Base.metadata.create_all(bind=settings.engine)


def get_db():
    db = settings.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/tasks", response_model=t.List[schemas.Task])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks


@app.post("/tasks", response_model=schemas.Task, status_code=201)
def create_task(task_data: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(**task_data.dict())
    db.add(task)
    db.commit()
    return task


@app.get("/tasks/{id}", response_model=schemas.Task)
def get_tasks_by(id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(models.Task).get(id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id: {id} not found")
    return task


@app.patch("/tasks/{id}", response_model=schemas.Task)
def patch_task(
    id: uuid.UUID,
    task_data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(models.Task).with_for_update().get(id)

    if (task_data.status == models.TaskStatus.IN_PROGRESS) and (
        task.status == models.TaskStatus.TODO
    ):
        task.start_time = utils.current_datetime()
    elif (task_data.status == models.TaskStatus.DONE) and (
        task.status == models.TaskStatus.IN_PROGRESS
    ):
        task.end_time = utils.current_datetime()
    else:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden update status for task with id: {id}",
        )

    task.status = task_data.status
    db.commit()
    return task


handler = Mangum(app=app)
