class TestArgumentGroups:
    def test_create_argument_group(self, client, sample_topic):
        resp = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"],
            "canonical_title": "Health risks of smoking",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["canonical_title"] == "Health risks of smoking"
        assert data["topic_id"] == sample_topic["id"]

    def test_create_argument_group_with_description(self, client, sample_topic):
        resp = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"],
            "canonical_title": "Economic impact",
            "description": "Arguments about economic consequences.",
        })
        assert resp.status_code == 201
        assert resp.json()["description"] == "Arguments about economic consequences."

    def test_list_argument_groups(self, client, sample_topic):
        client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group A",
        })
        client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group B",
        })
        resp = client.get("/api/argument-groups/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_argument_groups_by_topic(self, client, sample_user, sample_topic):
        t2 = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group A",
        })
        client.post("/api/argument-groups/", json={
            "topic_id": t2["id"], "canonical_title": "Group B",
        })
        resp = client.get(f"/api/argument-groups/?topic_id={sample_topic['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_argument_group(self, client, sample_topic):
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Test Group",
        }).json()
        resp = client.get(f"/api/argument-groups/{group['id']}")
        assert resp.status_code == 200
        assert resp.json()["canonical_title"] == "Test Group"

    def test_get_argument_group_not_found(self, client):
        resp = client.get("/api/argument-groups/9999")
        assert resp.status_code == 404

    def test_update_argument_group(self, client, sample_topic):
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Original",
        }).json()
        resp = client.patch(f"/api/argument-groups/{group['id']}", json={
            "canonical_title": "Updated",
        })
        assert resp.status_code == 200
        assert resp.json()["canonical_title"] == "Updated"

    def test_update_argument_group_not_found(self, client):
        resp = client.patch("/api/argument-groups/9999", json={
            "canonical_title": "Nope",
        })
        assert resp.status_code == 404

    def test_delete_argument_group(self, client, sample_topic):
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "To delete",
        }).json()
        resp = client.delete(f"/api/argument-groups/{group['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/api/argument-groups/{group['id']}")
        assert resp.status_code == 404

    def test_delete_argument_group_not_found(self, client):
        resp = client.delete("/api/argument-groups/9999")
        assert resp.status_code == 404

    def test_delete_group_keeps_nodes(self, client, sample_user, sample_topic):
        """Deleting a group should not delete its argument nodes."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Temp group",
        }).json()
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Grouped argument",
            "position": "PRO",
            "argument_group_id": group["id"],
        }).json()
        client.delete(f"/api/argument-groups/{group['id']}")
        # Argument should still exist with group_id cleared
        resp = client.get(f"/api/arguments/{arg['id']}")
        assert resp.status_code == 200
        assert resp.json()["argument_group_id"] is None

