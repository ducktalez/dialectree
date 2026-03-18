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
        # New defaults
        assert data["visibility"] == "VISIBLE"
        assert data["statement_type"] == "UNCLASSIFIED"
        assert data["position_score"] is None
        assert data["claim"] is None

    # ── Anatomy (Phase 0.1) ───────────────────────────────────────

    def test_create_argument_with_anatomy(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Migration ist wirtschaftlich notwendig",
            "position": "PRO",
            "claim": "Unsere Gesellschaft ist auf Migration angewiesen.",
            "reason": "Es gibt zu wenig Menschen, die diese Jobs machen wollen.",
            "example": "Allein die Krankenversorgung würde zusammenbrechen.",
            "implication": "Also ist Migration wirtschaftlich notwendig.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["claim"] == "Unsere Gesellschaft ist auf Migration angewiesen."
        assert data["reason"] == "Es gibt zu wenig Menschen, die diese Jobs machen wollen."
        assert data["example"] == "Allein die Krankenversorgung würde zusammenbrechen."
        assert data["implication"] == "Also ist Migration wirtschaftlich notwendig."

    def test_anatomy_in_tree(self, client, sample_user, sample_topic):
        client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "With anatomy",
            "position": "PRO",
            "claim": "Test claim",
            "reason": "Test reason",
        })
        resp = client.get(f"/api/topics/{sample_topic['id']}/tree")
        assert resp.status_code == 200
        nodes = resp.json()
        assert len(nodes) >= 1
        node = nodes[0]
        assert node["claim"] == "Test claim"
        assert node["reason"] == "Test reason"

    def test_update_anatomy(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "claim": "Updated claim",
            "reason": "Updated reason",
        })
        assert resp.status_code == 200
        assert resp.json()["claim"] == "Updated claim"
        assert resp.json()["reason"] == "Updated reason"

    # ── Visibility (Phase 0.2) ────────────────────────────────────

    def test_hide_argument(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "visibility": "MOD_HIDDEN",
            "hidden_reason": "Spam content",
        })
        assert resp.status_code == 200
        assert resp.json()["visibility"] == "MOD_HIDDEN"
        assert resp.json()["hidden_reason"] == "Spam content"

    def test_hidden_excluded_from_tree(self, client, sample_user, sample_topic):
        # Create two arguments
        a1 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Visible", "position": "PRO",
        }).json()
        a2 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Hidden", "position": "CONTRA",
        }).json()
        # Hide the second one
        client.patch(f"/api/arguments/{a2['id']}", json={
            "visibility": "VOTED_DOWN", "hidden_reason": "Community downvoted",
        })
        # Default tree should exclude hidden
        tree = client.get(f"/api/topics/{sample_topic['id']}/tree").json()
        ids = [n["id"] for n in tree]
        assert a1["id"] in ids
        assert a2["id"] not in ids
        # With show_hidden=true should include it
        tree_all = client.get(f"/api/topics/{sample_topic['id']}/tree?show_hidden=true").json()
        ids_all = [n["id"] for n in tree_all]
        assert a2["id"] in ids_all

    def test_invalid_visibility(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "visibility": "BOGUS",
        })
        assert resp.status_code == 400

    # ── Statement Type (Phase 0.6) ────────────────────────────────

    def test_create_with_statement_type(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Normative claim",
            "position": "PRO",
            "statement_type": "NORMATIVE",
        })
        assert resp.status_code == 201
        assert resp.json()["statement_type"] == "NORMATIVE"

    def test_invalid_statement_type(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Bad type",
            "position": "PRO",
            "statement_type": "FAKE",
        })
        assert resp.status_code == 400

    def test_statement_type_in_tree(self, client, sample_user, sample_topic):
        client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Factual",
            "position": "PRO",
            "statement_type": "POSITIVE",
        })
        tree = client.get(f"/api/topics/{sample_topic['id']}/tree").json()
        assert tree[0]["statement_type"] == "POSITIVE"

    # ── Continuous Position (Phase 0.7) ───────────────────────────

    def test_position_score_derives_position(self, client, sample_user, sample_topic):
        # Score 0.9 → PRO
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Strongly pro",
            "position": "NEUTRAL",  # should be overridden by score
            "position_score": 0.9,
        })
        assert resp.status_code == 201
        assert resp.json()["position"] == "PRO"
        assert resp.json()["position_score"] == 0.9

    def test_position_score_contra(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Strongly contra",
            "position": "PRO",
            "position_score": 0.1,
        })
        assert resp.json()["position"] == "CONTRA"

    def test_position_score_neutral(self, client, sample_user, sample_topic):
        resp = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Middle ground",
            "position": "PRO",
            "position_score": 0.5,
        })
        assert resp.json()["position"] == "NEUTRAL"

    def test_update_position_score(self, client, sample_argument):
        resp = client.patch(f"/api/arguments/{sample_argument['id']}", json={
            "position_score": 0.2,
        })
        assert resp.status_code == 200
        assert resp.json()["position"] == "CONTRA"  # auto-derived

    # ── Existing tests (unchanged) ────────────────────────────────

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

