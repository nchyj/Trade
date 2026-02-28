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
