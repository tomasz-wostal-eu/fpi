import pytest
from fastapi.testclient import TestClient
from fpi.main import app

client = TestClient(app)

def test_read_plants():
    response = client.get("/plants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Assuming it returns a list of plants

def test_create_plant():
    new_plant = {"name": "Sunflower", "latin_name": "Helianthus"}
    response = client.post("/plants/", json=new_plant)
    assert response.status_code == 200
    plant_data = response.json()
    
    # If you're using a Pydantic model in response, use model_dump instead of dict()
    assert plant_data["name"] == "Sunflower"
    assert plant_data["latin_name"] == "Helianthus"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200

def test_read_nonexistent_plant():
    response = client.get("/plants/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Plant not found"}

def test_update_nonexistent_plant():
    updated_plant = {"name": "Non-existent Plant", "latin_name": "Non-existent Latin Name"}
    response = client.put("/plants/9999", json=updated_plant)
    assert response.status_code == 404
    assert response.json() == {"detail": "Plant not found"}

def test_delete_nonexistent_plant():
    response = client.delete("/plants/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Plant not found"}