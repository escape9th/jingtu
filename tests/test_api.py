from fastapi.testclient import TestClient

from jingtu.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_classify_abuse():
    r = client.post("/classify", json={"text": "你是个傻逼", "strength": "standard"})
    assert r.status_code == 200
    data = r.json()
    assert "abuse" in data["labels"]
    assert data["blocked"] is True


def test_classify_normal():
    r = client.post("/classify", json={"text": "今天天气不错", "strength": "standard"})
    data = r.json()
    assert data["labels"] == ["normal"]
    assert data["blocked"] is False


def test_classify_mild_does_not_block_sarcasm():
    # 阴阳怪气 severity 0.5：mild 不拦，strict 拦
    r = client.post("/classify", json={"text": "不会吧不会吧，就这？", "strength": "mild"})
    assert r.json()["blocked"] is False
    r2 = client.post("/classify", json={"text": "不会吧不会吧，就这？", "strength": "strict"})
    assert r2.json()["blocked"] is True


def test_batch():
    r = client.post("/classify_batch", json={"texts": ["你是个傻逼", "今天天气不错"], "strength": "standard"})
    data = r.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["blocked"] is True
    assert data["results"][1]["blocked"] is False
