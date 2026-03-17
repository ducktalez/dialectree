class TestTopics:
    def test_create_topic(self, client, sample_user):
        resp = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Should smoking be banned?",
            "description": "A debate about smoking regulation.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Should smoking be banned?"
        assert data["created_by"] == sample_user["id"]

    def test_list_topics(self, client, sample_topic):
        resp = client.get("/api/topics/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_topic(self, client, sample_topic):
        resp = client.get(f"/api/topics/{sample_topic['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Topic"

    def test_get_topic_not_found(self, client):
        resp = client.get("/api/topics/9999")
        assert resp.status_code == 404

    def test_delete_topic(self, client, sample_topic):
        resp = client.delete(f"/api/topics/{sample_topic['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/api/topics/{sample_topic['id']}")
        assert resp.status_code == 404

    def test_get_argument_tree(self, client, sample_user, sample_topic):
        # Create root argument
        r1 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Root arg", "position": "PRO",
        }).json()
        # Create child argument
        client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "parent_id": r1["id"],
            "title": "Child arg", "position": "CONTRA",
        })
        resp = client.get(f"/api/topics/{sample_topic['id']}/tree")
        assert resp.status_code == 200
        tree = resp.json()
        assert len(tree) >= 1
        # Find the root node and check it has a child
        root = next(n for n in tree if n["title"] == "Root arg")
        assert len(root["children"]) == 1
        assert root["children"][0]["title"] == "Child arg"

