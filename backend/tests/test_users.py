class TestUsers:
    def test_create_user(self, client):
        resp = client.post("/api/users/", json={
            "username": "alice", "email": "alice@test.com", "password": "pw123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@test.com"
        assert "id" in data

    def test_duplicate_username(self, client):
        client.post("/api/users/", json={
            "username": "alice", "email": "alice@test.com", "password": "pw123"
        })
        resp = client.post("/api/users/", json={
            "username": "alice", "email": "other@test.com", "password": "pw123"
        })
        assert resp.status_code == 400

    def test_duplicate_email(self, client):
        client.post("/api/users/", json={
            "username": "alice", "email": "same@test.com", "password": "pw123"
        })
        resp = client.post("/api/users/", json={
            "username": "bob", "email": "same@test.com", "password": "pw123"
        })
        assert resp.status_code == 400

    def test_list_users(self, client, sample_user):
        resp = client.get("/api/users/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_user(self, client, sample_user):
        resp = client.get(f"/api/users/{sample_user['id']}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_get_user_not_found(self, client):
        resp = client.get("/api/users/9999")
        assert resp.status_code == 404

