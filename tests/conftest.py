from fastapi.testclient import TestClient

import pytest

from src import main, models, settings


@pytest.fixture(autouse=True)
def clear_db():
    db = settings.SessionLocal()
    db.query(models.Task).delete()
    db.commit()


@pytest.fixture()
def client():
    return TestClient(main.app)
