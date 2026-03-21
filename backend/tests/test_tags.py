class TestTags:
    def test_create_tag(self, client):
        resp = client.post("/api/tags/", json={"name": "Gesundheit"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Gesundheit"
        assert resp.json()["category"] == "OTHER"  # default

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

    def test_create_tag_with_category(self, client):
        resp = client.post("/api/tags/", json={"name": "Ethik", "category": "DOMAIN"})
        assert resp.status_code == 201
        assert resp.json()["category"] == "DOMAIN"

    def test_create_tag_with_moral_foundation_category(self, client):
        resp = client.post("/api/tags/", json={
            "name": "Gerechtigkeit",
            "moral_foundation": "FAIRNESS",
            "category": "MORAL_FOUNDATION",
        })
        assert resp.status_code == 201
        assert resp.json()["moral_foundation"] == "FAIRNESS"
        assert resp.json()["category"] == "MORAL_FOUNDATION"

    def test_invalid_category(self, client):
        resp = client.post("/api/tags/", json={"name": "Bad", "category": "INVALID_CAT"})
        assert resp.status_code == 400

    def test_assign_tag_with_origin(self, client, sample_argument):
        tag = client.post("/api/tags/", json={"name": "OriginTag"}).json()
        resp = client.post("/api/tags/assign", json={
            "tag_id": tag["id"],
            "argument_node_id": sample_argument["id"],
            "origin": "MODERATOR",
        })
        assert resp.status_code == 201

    def test_assign_tag_default_origin(self, client, sample_argument):
        tag = client.post("/api/tags/", json={"name": "DefaultTag"}).json()
        resp = client.post("/api/tags/assign", json={
            "tag_id": tag["id"],
            "argument_node_id": sample_argument["id"],
        })
        assert resp.status_code == 201

    def test_assign_tag_invalid_origin(self, client, sample_argument):
        tag = client.post("/api/tags/", json={"name": "BadOrigin"}).json()
        resp = client.post("/api/tags/assign", json={
            "tag_id": tag["id"],
            "argument_node_id": sample_argument["id"],
            "origin": "INVALID_ORIGIN",
        })
        assert resp.status_code == 400

    def test_tag_with_category_in_tree(self, client, sample_user, sample_argument):
        """Verify that tag category and origin appear in the tree response."""
        tag = client.post("/api/tags/", json={
            "name": "TreeTag", "category": "DOMAIN",
        }).json()
        client.post("/api/tags/assign", json={
            "tag_id": tag["id"],
            "argument_node_id": sample_argument["id"],
            "origin": "AI",
        })
        topic_id = sample_argument["topic_id"]
        resp = client.get(f"/api/topics/{topic_id}/tree")
        assert resp.status_code == 200
        tree = resp.json()
        node = next(n for n in tree if n["id"] == sample_argument["id"])
        assert len(node["tags"]) == 1
        tag_info = node["tags"][0]
        assert tag_info["tag_name"] == "TreeTag"
        assert tag_info["category"] == "DOMAIN"
        assert tag_info["origin"] == "AI"
