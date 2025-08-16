import json

from starlette.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_ai_models_crud_flow(monkeypatch):
	# Mock auth by bypassing dependency if needed; here assume public for simplicity
	base = "/api/v1/ai-models"

	# Create
	payload = {
		"name": "Test Model",
		"provider": "openai",
		"model_key": "gpt-4",
		"display_name": "OpenAI GPT-4",
		"description": "Test",
		"max_tokens": 8192,
		"cost_per_1k_tokens": 0.03,
		"capabilities": ["chat", "reasoning"],
	}
	r = client.post(f"{base}/", json=payload)
	assert r.status_code in (200, 201)
	created = r.json()
	assert created["name"] == "Test Model"
	mid = created["id"]

	# List
	r = client.get(f"{base}/")
	assert r.status_code == 200
	assert any(m["id"] == mid for m in r.json())

	# Update
	r = client.put(f"{base}/{mid}", json={"description": "Updated"})
	assert r.status_code == 200
	assert r.json()["description"] == "Updated"

	# Toggle
	r = client.put(f"{base}/{mid}/toggle", json={"isActive": False})
	assert r.status_code == 200
	assert r.json()["is_active"] is False

	# Set default
	r = client.put(f"{base}/{mid}/default")
	assert r.status_code == 200
	assert r.json()["is_default"] is True

	# Delete
	r = client.delete(f"{base}/{mid}")
	assert r.status_code == 200