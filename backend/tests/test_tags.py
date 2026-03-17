class TestTags:
    def test_create_tag(self, client):
        resp = client.post("/api/tags/", json={"name": "Gesundheit"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Gesundheit"

    def test_create_tag_with_moral_foundation(self, client):
        resp = client.post("/api/tags/", json={"name": "Fürsorge", "moral_foundation": "CARE"})
        assert resp.status_code == 201
        assert resp.json()["moral_foundation"] == "CARE"

    def test_duplicate_tag(self, client):
        client.post("/api/tags/", json={"name": "Gesundheit"})
        resp = client.post("/api/tags/", json={"name": "Gesundheit"})
        assert resp.status_code == 400

    def test_assign_tag(self, client, sample_argument):
        tag = client.post("/api/tags/", json={"name": "TestTag"}).json()
        resp = client.post("/api/tags/assign", json={
            "tag_id": tag["id"], "argument_node_id": sample_argument["id"],
        })
        assert resp.status_code == 201

    def test_assign_tag_duplicate(self, client, sample_argument):
        tag = client.post("/api/tags/", json={"name": "TestTag"}).json()
        client.post("/api/tags/assign", json={
            "tag_id": tag["id"], "argument_node_id": sample_argument["id"],
        })
        resp = client.post("/api/tags/assign", json={
            "tag_id": tag["id"], "argument_node_id": sample_argument["id"],
        })
        assert resp.status_code == 400

    def test_vote_on_tag(self, client, sample_user, sample_argument):
        tag = client.post("/api/tags/", json={"name": "TestTag"}).json()
        client.post("/api/tags/assign", json={
            "tag_id": tag["id"], "argument_node_id": sample_argument["id"],
        })
        resp = client.post(f"/api/tags/vote?user_id={sample_user['id']}", json={
            "tag_id": tag["id"], "argument_node_id": sample_argument["id"], "value": 1,
        })
        assert resp.status_code == 201

    def test_list_tags(self, client):
        client.post("/api/tags/", json={"name": "Tag1"})
        client.post("/api/tags/", json={"name": "Tag2"})
        resp = client.get("/api/tags/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

