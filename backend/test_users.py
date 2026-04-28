import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()
    yield
    # We do not drop everything because other tests might need data, 
    # but for simple isolation we can just clean the users table.
    # Base.metadata.drop_all(bind=engine)

def test_register_and_login():
    res = client.post("/api/users/register", json={"username": "testuser", "email": "test@test.com", "password": "password"})
    assert res.status_code == 201

    res = client.post("/api/users/login", json={"username": "testuser", "password": "password"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    
    # Ensure HttpOnly cookie is set
    assert "access_token" in client.cookies

    # The client automatically sends the cookie upon subsequent requests
    res_me = client.get("/api/users/me")
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "testuser"

    # Logout
    res_logout = client.post("/api/users/logout")
    assert res_logout.status_code == 200
    # Cookie should be unset/expired
    
    # Verify unauthorized if no cookie
    client.cookies.clear()
    res_unauth = client.get("/api/users/me")
    assert res_unauth.status_code == 401
