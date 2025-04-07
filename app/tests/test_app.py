# test_app.py
import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_create_and_get_task(client):
    # Create a task
    response = client.post('/api/tasks', 
                          json={'title': 'Test Task', 'description': 'Test Description'})
    assert response.status_code == 201
    data = json.loads(response.data)
    task_id = data['id']
    
    # Get the task
    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Test Task'
    assert data['description'] == 'Test Description'