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
            "evidence_type": "JOURNALISM",
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

    def test_default_quality_score(self, client, sample_user, sample_argument):
        """When quality_score is not provided, it should default from evidence type."""
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "STUDY",
            "title": "No explicit quality",
        })
        assert resp.status_code == 201
        assert resp.json()["quality_score"] == 0.9  # default for STUDY

    def test_default_quality_anecdote(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "ANECDOTE",
            "title": "Personal story",
        })
        assert resp.status_code == 201
        assert resp.json()["quality_score"] == 0.3

    def test_explicit_quality_overrides_default(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "evidence_type": "ANECDOTE",
            "title": "High quality anecdote",
            "quality_score": 0.8,
        })
        assert resp.status_code == 201
        assert resp.json()["quality_score"] == 0.8

    def test_new_evidence_types(self, client, sample_user, sample_argument):
        """All new evidence types from taxonomy §7 should be accepted."""
        new_types = ["PROOF", "META_ANALYSIS", "LAW", "EXPERT_OPINION",
                     "JOURNALISM", "SURVEY", "HISTORICAL", "THOUGHT_EXPERIMENT",
                     "HEARSAY", "UNFALSIFIABLE", "FABRICATION"]
        for ev_type in new_types:
            resp = client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
                "argument_node_id": sample_argument["id"],
                "evidence_type": ev_type,
                "title": f"Test {ev_type}",
            })
            assert resp.status_code == 201, f"Failed for {ev_type}"

