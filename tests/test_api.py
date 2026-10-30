def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.is_json
    assert res.get_json() == {"status": "OK"}


def test_health_rejects_post(client):
    res = client.post("/health")
    assert res.status_code == 405
