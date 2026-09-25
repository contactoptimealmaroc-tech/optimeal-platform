import os
os.environ.setdefault("SECRET_KEY","test-secret-for-tests")
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    r=TestClient(app).get("/api/v1/health")
    assert r.status_code==200
    assert r.json()["status"]=="ok"

def test_public_site_is_served_without_auth():
    r=TestClient(app).get("/")
    assert r.status_code==200

def test_client_page_redirects_to_connexion_when_not_authenticated():
    r=TestClient(app, follow_redirects=False).get("/client")
    assert r.status_code==303
    assert r.headers["location"]=="/connexion"

def test_os_page_redirects_to_connexion_when_not_authenticated():
    r=TestClient(app, follow_redirects=False).get("/os")
    assert r.status_code==303
    assert r.headers["location"]=="/connexion"
