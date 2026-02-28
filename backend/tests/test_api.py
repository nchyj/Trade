from app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    resp = client.get('/api/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'


def test_market_data_endpoint():
    app = create_app()
    client = app.test_client()
    resp = client.get('/api/market-data')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_scheduler_task_create_and_list():
    app = create_app()
    client = app.test_client()

    create_resp = client.post('/api/scheduler/tasks', json={
        'name': 'test-market-pull',
        'task_type': 'market_pull',
        'interval_sec': 15,
    })
    assert create_resp.status_code == 201

    list_resp = client.get('/api/scheduler/tasks')
    assert list_resp.status_code == 200
    assert isinstance(list_resp.get_json(), list)
