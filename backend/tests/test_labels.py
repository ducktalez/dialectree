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

    def test_new_label_types(self, client, sample_user, sample_argument):
        """All extended label types from taxonomy §13 should be accepted."""
        new_types = ["MISSING_EVIDENCE", "OFF_TOPIC", "SPAM", "ANECDOTE",
                     "DUPLICATE", "CONTENTLESS", "SCOPE_VIOLATION",
                     "MANIPULATION", "INVALID"]
        for label_type in new_types:
            resp = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
                "argument_node_id": sample_argument["id"],
                "label_type": label_type,
                "justification": f"Test justification for {label_type}.",
            })
            assert resp.status_code == 201, f"Failed for {label_type}"

    def test_label_has_confirmed_field(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "label_type": "FALLACY",
            "justification": "Check confirmed field.",
        })
        data = resp.json()
        assert data["confirmed"] == 0
        assert data["confirmed_at"] is None

