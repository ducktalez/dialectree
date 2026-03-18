class TestArguments:
    def test_create_argument(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Test PRO argument",
            "position": "PRO",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test PRO argument"
        assert data["position"] == "PRO"
        assert data["parent_id"] is None

    def test_create_child_argument(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_argument["topic_id"],
            "parent_id": sample_argument["id"],
            "title": "Child argument",
            "position": "CONTRA",
        })
        assert resp.status_code == 201
        assert resp.json()["parent_id"] == sample_argument["id"]

    def test_invalid_position(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Bad position",
            "position": "INVALID",
        })
        assert resp.status_code == 400

    def test_parent_different_topic(self, client, sample_user, sample_argument):
        # Create second topic
        t2 = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": t2["id"],
            "parent_id": sample_argument["id"],
            "title": "Cross-topic child",
            "position": "PRO",
        })
        assert resp.status_code == 400

    def test_list_arguments_by_topic(self, client, sample_argument):
        resp = client.get(f"/api/arguments/?topic_id={sample_argument['topic_id']}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_argument(self, client, sample_argument):
        resp = client.get(f"/api/arguments/{sample_argument['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Argument"

    def test_delete_argument(self, client, sample_argument):
        resp = client.delete(f"/api/arguments/{sample_argument['id']}")
        assert resp.status_code == 204

    def test_update_argument(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "title": "Updated title",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"
        assert resp.json()["position"] == "PRO"  # unchanged

    def test_update_argument_position(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "position": "CONTRA",
        })
        assert resp.status_code == 200
        assert resp.json()["position"] == "CONTRA"

    def test_update_argument_invalid_position(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "position": "INVALID",
        })
        assert resp.status_code == 400

    def test_update_argument_not_found(self, client):
        resp = client.patch("/api/arguments/9999", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_cascade_delete_subtree(self, client, sample_user, sample_topic):
        """Deleting a parent argument should delete its children."""
        parent = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Parent", "position": "PRO",
        }).json()
        child = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "parent_id": parent["id"],
            "title": "Child", "position": "CONTRA",
        }).json()
        client.delete(f"/api/arguments/{parent['id']}")
        assert client.get(f"/api/arguments/{child['id']}").status_code == 404

    def test_cascade_delete_votes_comments(self, client, sample_user, sample_topic):
        """Deleting an argument should delete its votes and comments."""
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Temp", "position": "PRO",
        }).json()
        client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "value": 1,
        })
        client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "text": "Will be deleted",
        })
        client.delete(f"/api/arguments/{arg['id']}")
        assert len(client.get(f"/api/votes/?argument_node_id={arg['id']}").json()) == 0
        assert len(client.get(f"/api/comments/?argument_node_id={arg['id']}").json()) == 0

