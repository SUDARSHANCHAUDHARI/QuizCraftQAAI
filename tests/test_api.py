import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("API_TOKEN", "test-token")
# app.services.gemini reads the key at import time; the model itself is mocked below.
os.environ.setdefault("GEMINI_API_KEY", "test-key")
from app.main import app
from app.services import gemini

client = TestClient(app, headers={"X-API-Token": os.environ["API_TOKEN"]})


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    # Replace the Gemini model so tests never touch the network or need a real key.
    model = MagicMock()
    model.generate_content.return_value.text = (
        '```json\n[{"type": "mcq", "prompt": "Q?", "options": ["a", "b", "c", "d"], '
        '"correctAnswer": "a", "explanation": "e", "difficulty": "easy"}]\n```'
    )
    monkeypatch.setattr(gemini, "model", model)
    return model

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate_requires_token():
    response = TestClient(app).post("/generate", json={"text": "x"})
    assert response.status_code == 401

def test_generate_questions():
    payload = {
        "text": "Software testing is a process.",
        "question_type": "mcq",
        "count": 1
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert "questions" in response.json()
    assert isinstance(response.json()["questions"], list)

def test_study_plan():
    payload = {
        "text": "Software testing syllabus.",
        "weeks": 2,
        "weak_topics": ["unit testing"]
    }
    response = client.post("/study-plan", json=payload)
    assert response.status_code == 200
    assert "plan" in response.json()
    assert isinstance(response.json()["plan"], str)
