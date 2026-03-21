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

    def test_get_argument_tree_enriched(self, client, sample_user, sample_topic):
        """Tree nodes should include tags, labels, evidence_count, comment_count, created_by."""
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Enriched arg", "position": "PRO",
        }).json()
        # Add tag
        tag = client.post("/api/tags/", json={"name": "Health"}).json()
        client.post("/api/tags/assign", json={
            "tag_id": tag["id"], "argument_node_id": arg["id"],
        })
        # Add label
        client.post(f"/api/labels/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "label_type": "FALLACY",
            "justification": "Straw man argument.",
        })
        # Add evidence
        client.post(f"/api/evidence/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "evidence_type": "STUDY",
            "title": "WHO Report",
        })
        # Add comment
        client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "text": "Interesting point.",
        })

        resp = client.get(f"/api/topics/{sample_topic['id']}/tree")
        assert resp.status_code == 200
        tree = resp.json()
        node = next(n for n in tree if n["title"] == "Enriched arg")
        assert any(t["tag_name"] == "Health" for t in node["tags"])
        assert node["tags"][0]["origin"] == "USER"
        assert "FALLACY" in node["labels"]
        assert node["evidence_count"] == 1
        assert node["comment_count"] == 1
        assert node["created_by"] == sample_user["id"]

    def test_update_topic(self, client, sample_topic):
        resp = client.patch(f"/api/topics/{sample_topic['id']}", json={
            "title": "Updated Title",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"
        assert resp.json()["description"] == sample_topic["description"]

    def test_update_topic_not_found(self, client):
        resp = client.patch("/api/topics/9999", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_cascade_delete_topic(self, client, sample_user):
        """Deleting a topic should cascade-delete arguments, votes, etc."""
        topic = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Cascade topic",
        }).json()
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": topic["id"], "title": "Cascade arg", "position": "PRO",
        }).json()
        vote = client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": arg["id"], "value": 1,
        }).json()
        client.delete(f"/api/topics/{topic['id']}")
        # Argument and vote should be gone
        assert client.get(f"/api/arguments/{arg['id']}").status_code == 404
        resp = client.get(f"/api/votes/?argument_node_id={arg['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 0

