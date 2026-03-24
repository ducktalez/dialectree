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


class TestZigzagView:
    """Tests for GET /api/topics/{id}/zigzag endpoint."""

    def test_zigzag_basic(self, client, sample_user, sample_topic):
        """Zigzag returns a flat, chronologically sorted list."""
        uid = sample_user["id"]
        tid = sample_topic["id"]
        a1 = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "title": "Opening claim", "position": "CONTRA",
            "conflict_zone": "VALUE", "position_score": 0.2,
        }).json()
        a2 = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "parent_id": a1["id"],
            "title": "Counter", "position": "PRO",
            "conflict_zone": "FACT", "edge_type": "REFRAME",
        }).json()

        resp = client.get(f"/api/topics/{tid}/zigzag")
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"]["id"] == tid
        assert len(data["steps"]) == 2
        # Chronological order
        assert data["steps"][0]["id"] == a1["id"]
        assert data["steps"][1]["id"] == a2["id"]
        # Fields present
        step1 = data["steps"][0]
        assert step1["conflict_zone"] == "VALUE"
        assert step1["position"] == "CONTRA"
        assert step1["position_score"] == 0.2
        step2 = data["steps"][1]
        assert step2["conflict_zone"] == "FACT"
        assert step2["edge_type"] == "REFRAME"
        assert step2["parent_id"] == a1["id"]

    def test_zigzag_siblings(self, client, sample_user, sample_topic):
        """Sibling_ids lists other nodes with the same parent_id."""
        uid = sample_user["id"]
        tid = sample_topic["id"]
        root = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "title": "Root", "position": "PRO",
        }).json()
        c1 = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "parent_id": root["id"],
            "title": "Child A", "position": "CONTRA",
        }).json()
        c2 = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "parent_id": root["id"],
            "title": "Child B", "position": "CONTRA",
        }).json()

        resp = client.get(f"/api/topics/{tid}/zigzag")
        steps = resp.json()["steps"]
        child_a = next(s for s in steps if s["id"] == c1["id"])
        child_b = next(s for s in steps if s["id"] == c2["id"])
        assert c2["id"] in child_a["sibling_ids"]
        assert c1["id"] in child_b["sibling_ids"]
        # Root has no siblings (no parent)
        root_step = next(s for s in steps if s["id"] == root["id"])
        assert root_step["sibling_ids"] == []

    def test_zigzag_edge_attack(self, client, sample_user, sample_topic):
        """Edge attack flag is correctly returned."""
        uid = sample_user["id"]
        tid = sample_topic["id"]
        a1 = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "title": "Claim", "position": "PRO",
        }).json()
        atk = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "parent_id": a1["id"],
            "title": "Edge attack!", "position": "CONTRA",
            "is_edge_attack": True, "conflict_zone": "VALUE",
        }).json()

        resp = client.get(f"/api/topics/{tid}/zigzag")
        steps = resp.json()["steps"]
        atk_step = next(s for s in steps if s["id"] == atk["id"])
        assert atk_step["is_edge_attack"] is True

    def test_zigzag_vote_score(self, client, sample_user, sample_topic):
        """Vote scores are computed in the zigzag response."""
        uid = sample_user["id"]
        tid = sample_topic["id"]
        a = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "title": "Votable", "position": "PRO",
        }).json()
        client.post(f"/api/votes/?user_id={uid}", json={
            "argument_node_id": a["id"], "value": 1,
        })
        resp = client.get(f"/api/topics/{tid}/zigzag")
        step = next(s for s in resp.json()["steps"] if s["id"] == a["id"])
        assert step["vote_score"] == 1

    def test_zigzag_opens_conflict(self, client, sample_user, sample_topic):
        """opens_conflict field is returned correctly."""
        uid = sample_user["id"]
        tid = sample_topic["id"]
        a = client.post(f"/api/arguments/?user_id={uid}", json={
            "topic_id": tid, "title": "Splits discussion", "position": "PRO",
            "opens_conflict": "Sub-topic Alpha",
        }).json()
        resp = client.get(f"/api/topics/{tid}/zigzag")
        step = next(s for s in resp.json()["steps"] if s["id"] == a["id"])
        assert step["opens_conflict"] == "Sub-topic Alpha"

    def test_zigzag_not_found(self, client):
        resp = client.get("/api/topics/9999/zigzag")
        assert resp.status_code == 404


