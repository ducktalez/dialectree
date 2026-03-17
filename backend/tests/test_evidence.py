class TestEvidence:
    def test_create_evidence(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "STUDY",
            "title": "WHO Report",
            "url": "https://who.int/report",
            "quality_score": 0.95,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["evidence_type"] == "STUDY"
        assert data["quality_score"] == 0.95

    def test_invalid_evidence_type(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "INVALID",
            "title": "Bad type",
        })
        assert resp.status_code == 400

    def test_quality_score_out_of_range(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "STATISTIC",
            "title": "Bad score",
            "quality_score": 1.5,
        })
        assert resp.status_code == 400

    def test_list_evidence(self, client, sample_user, sample_argument):
        client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "ARTICLE",
            "title": "Article 1",
        })
        resp = client.get(f"/api/evidence/?argument_node_id={sample_argument['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_delete_evidence(self, client, sample_user, sample_argument):
        ev = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "STUDY",
            "title": "To delete",
        }).json()
        resp = client.delete(f"/api/evidence/{ev['id']}")
        assert resp.status_code == 204

