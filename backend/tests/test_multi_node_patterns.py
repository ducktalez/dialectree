class TestMultiNodePatterns:
    def test_create_pattern(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_argument["topic_id"],
            "name": "Gish gallop in health debate",
            "pattern_type": "GISH_GALLOP",
            "member_ids": [sample_argument["id"]],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Gish gallop in health debate"
        assert data["pattern_type"] == "GISH_GALLOP"
        assert sample_argument["id"] in data["member_ids"]

    def test_create_pattern_no_members(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Empty pattern",
            "pattern_type": "OTHER",
        })
        assert resp.status_code == 201
        assert resp.json()["member_ids"] == []

    def test_create_pattern_invalid_type(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Bad type",
            "pattern_type": "NONEXISTENT",
        })
        assert resp.status_code == 400

    def test_create_pattern_member_wrong_topic(self, client, sample_user, sample_argument):
        t2 = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        resp = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": t2["id"],
            "name": "Cross-topic pattern",
            "pattern_type": "OTHER",
            "member_ids": [sample_argument["id"]],
        })
        assert resp.status_code == 400

    def test_create_pattern_member_not_found(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Ghost members",
            "pattern_type": "OTHER",
            "member_ids": [9999],
        })
        assert resp.status_code == 404

    def test_list_patterns(self, client, sample_user, sample_topic):
        client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Pattern A",
            "pattern_type": "OTHER",
        })
        client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Pattern B",
            "pattern_type": "GISH_GALLOP",
        })
        resp = client.get("/api/patterns/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_patterns_by_topic(self, client, sample_user, sample_topic):
        t2 = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Pattern A",
            "pattern_type": "OTHER",
        })
        client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": t2["id"],
            "name": "Pattern B",
            "pattern_type": "OTHER",
        })
        resp = client.get(f"/api/patterns/?topic_id={sample_topic['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_pattern(self, client, sample_user, sample_topic):
        p = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "Test pattern",
            "pattern_type": "CREEPING_RELATIVIZATION",
        }).json()
        resp = client.get(f"/api/patterns/{p['id']}")
        assert resp.status_code == 200
        assert resp.json()["pattern_type"] == "CREEPING_RELATIVIZATION"

    def test_get_pattern_not_found(self, client):
        resp = client.get("/api/patterns/9999")
        assert resp.status_code == 404

    def test_delete_pattern(self, client, sample_user, sample_topic):
        p = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "name": "To delete",
            "pattern_type": "OTHER",
        }).json()
        resp = client.delete(f"/api/patterns/{p['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/api/patterns/{p['id']}")
        assert resp.status_code == 404

    def test_delete_pattern_not_found(self, client):
        resp = client.delete("/api/patterns/9999")
        assert resp.status_code == 404

    def test_cascade_delete_with_topic(self, client, sample_user):
        """Deleting a topic should also delete its patterns."""
        topic = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Temp topic",
        }).json()
        p = client.post(f"/api/patterns/?user_id={sample_user['id']}", json={
            "topic_id": topic["id"],
            "name": "Temp pattern",
            "pattern_type": "OTHER",
        }).json()
        client.delete(f"/api/topics/{topic['id']}")
        resp = client.get(f"/api/patterns/{p['id']}")
        assert resp.status_code == 404

