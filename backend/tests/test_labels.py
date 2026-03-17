class TestLabels:
    def test_create_label(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "FALLACY",
            "justification": "This is a straw man argument because it misrepresents the original claim.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["label_type"] == "FALLACY"
        assert "straw man" in data["justification"]

    def test_label_requires_justification(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "FALLACY",
            "justification": "   ",
        })
        assert resp.status_code == 400

    def test_invalid_label_type(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "NONEXISTENT",
            "justification": "Reason.",
        })
        assert resp.status_code == 400

    def test_list_labels(self, client, sample_user, sample_argument):
        client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "DOUBLE_STANDARD",
            "justification": "Applies different standards to similar situations.",
        })
        resp = client.get(f"/api/labels/?argument_node_id={sample_argument['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_delete_label(self, client, sample_user, sample_argument):
        label = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "FALLACY",
            "justification": "To be deleted.",
        }).json()
        resp = client.delete(f"/api/labels/{label['id']}")
        assert resp.status_code == 204

