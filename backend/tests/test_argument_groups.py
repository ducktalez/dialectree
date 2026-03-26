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

    def test_merge_arguments(self, client, sample_user, sample_topic):
        """Merge two arguments into a group."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Merge group",
        }).json()
        a1 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Arg1", "position": "PRO",
        }).json()
        a2 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Arg2", "position": "PRO",
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/merge", json={
            "argument_node_ids": [a1["id"], a2["id"]],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["merged"] == 2
        assert data["group_id"] == group["id"]
        # Verify both arguments are in the group
        assert client.get(f"/api/arguments/{a1['id']}").json()["argument_group_id"] == group["id"]
        assert client.get(f"/api/arguments/{a2['id']}").json()["argument_group_id"] == group["id"]

    def test_merge_group_not_found(self, client):
        resp = client.post("/api/argument-groups/9999/merge", json={
            "argument_node_ids": [1],
        })
        assert resp.status_code == 404

    def test_merge_node_not_found(self, client, sample_topic):
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group",
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/merge", json={
            "argument_node_ids": [9999],
        })
        assert resp.status_code == 404

    def test_merge_node_wrong_topic(self, client, sample_user, sample_topic):
        """Nodes must belong to the same topic as the group."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group",
        }).json()
        other_topic = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": other_topic["id"], "title": "Wrong topic", "position": "PRO",
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/merge", json={
            "argument_node_ids": [arg["id"]],
        })
        assert resp.status_code == 400

    def test_unmerge_argument(self, client, sample_user, sample_topic):
        """Unmerge an argument from a group."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Unmerge group",
        }).json()
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Grouped", "position": "PRO",
            "argument_group_id": group["id"],
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/unmerge/{arg['id']}")
        assert resp.status_code == 200
        assert resp.json()["unmerged"] == arg["id"]
        # Verify argument is no longer in the group
        assert client.get(f"/api/arguments/{arg['id']}").json()["argument_group_id"] is None

    def test_unmerge_group_not_found(self, client):
        resp = client.post("/api/argument-groups/9999/unmerge/1")
        assert resp.status_code == 404

    def test_unmerge_node_not_found(self, client, sample_topic):
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group",
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/unmerge/9999")
        assert resp.status_code == 404

    def test_unmerge_node_not_in_group(self, client, sample_user, sample_topic):
        """Cannot unmerge a node that isn't in this group."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Group",
        }).json()
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Not grouped", "position": "PRO",
        }).json()
        resp = client.post(f"/api/argument-groups/{group['id']}/unmerge/{arg['id']}")
        assert resp.status_code == 400

    def test_merge_then_verify_in_tree(self, client, sample_user, sample_topic):
        """Merged arguments should show argument_group_id in the tree response."""
        group = client.post("/api/argument-groups/", json={
            "topic_id": sample_topic["id"], "canonical_title": "Tree group",
        }).json()
        a1 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Grouped arg", "position": "PRO",
        }).json()
        client.post(f"/api/argument-groups/{group['id']}/merge", json={
            "argument_node_ids": [a1["id"]],
        })
        tree = client.get(f"/api/topics/{sample_topic['id']}/tree").json()
        assert any(node["argument_group_id"] == group["id"] for node in tree)

