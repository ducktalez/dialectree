import os

os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def _override():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_user(client):
    resp = client.post("/api/users/", json={
        "username": "testuser", "email": "test@example.com", "password": "secret"
    })
    return resp.json()


@pytest.fixture()
def sample_topic(client, sample_user):
    resp = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
        "title": "Test Topic", "description": "A test topic"
    })
    return resp.json()


@pytest.fixture()
def sample_argument(client, sample_user, sample_topic):
    resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
        "topic_id": sample_topic["id"],
        "title": "Test Argument",
        "description": "A test argument",
        "position": "PRO",
    })
    return resp.json()




