import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DB = "test_api.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB}"

engine_test = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # obriši staru test bazu
    if os.path.exists(TEST_DB):
        engine_test.dispose()
        os.remove(TEST_DB)

    # napravi tabele u test bazi
    Base.metadata.create_all(bind=engine_test)

    # override dependency
    app.dependency_overrides[get_db] = override_get_db

    yield

    # cleanup
    app.dependency_overrides.clear()

    # VAŽNO za Windows: zatvori sve konekcije ka sqlite fajlu
    engine_test.dispose()

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB) 

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_crud_flow():
    # CREATE
    payload = {
        "marka": "Audi",
        "model": "A4",
        "godiste": 2018,
        "tablice": "BG-123-AA"
    }
    r = client.post("/vozila", json=payload)
    assert r.status_code == 201
    created = r.json()
    vozilo_id = created["id"]
    assert created["marka"] == "Audi"

    # READ (list)
    r = client.get("/vozila")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # READ (single)
    r = client.get(f"/vozila/{vozilo_id}")
    assert r.status_code == 200
    assert r.json()["tablice"] == "BG-123-AA"

    # SEARCH
    r = client.get("/vozila/search", params={"marka": "Au"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # UPDATE
    payload_update = {
        "marka": "Audi",
        "model": "A6",
        "godiste": 2020,
        "tablice": "BG-123-AA"
    }
    r = client.put(f"/vozila/{vozilo_id}", json=payload_update)
    assert r.status_code == 200
    assert r.json()["model"] == "A6"
    assert r.json()["godiste"] == 2020

    # DELETE
    r = client.delete(f"/vozila/{vozilo_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True

    # READ after delete
    r = client.get(f"/vozila/{vozilo_id}")
    assert r.status_code == 404


def test_unique_tablice_conflict():
    payload = {
        "marka": "BMW",
        "model": "X5",
        "godiste": 2019,
        "tablice": "NP-999-ZZ"
    }
    r1 = client.post("/vozila", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/vozila", json=payload)
    assert r2.status_code == 409
