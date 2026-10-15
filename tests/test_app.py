import pytest
from app import config


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "test.db"))
    from app.main import create_app
    app = create_app(start_scheduler=False)
    return app.test_client()


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_metrics_endpoint(client):
    r = client.get("/metrics")
    assert r.status_code == 200 and b"crypto_polls_total" in r.data


def test_dashboard_loads(client):
    assert client.get("/").status_code == 200


def test_rule_create_and_delete(client):
    client.post("/rules", data={"coin": "bitcoin", "rule_type": "price_above", "value": "50000"})
    from app import db
    rules = db.list_rules()
    assert len(rules) == 1
    client.post(f"/rules/{rules[0]['id']}/delete")
    assert db.list_rules() == []
