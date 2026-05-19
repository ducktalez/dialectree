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


class TestArgumentSplit:
    """Z.2c — POST /api/arguments/{id}/split and PATCH /{id}/connect."""

    def _base(self, client, user, topic, parent_id=None):
        payload = {"topic_id": topic["id"], "title": "Base claim", "position": "PRO"}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        return client.post(f"/api/arguments/?user_id={user['id']}", json=payload).json()

    def test_split_creates_children_with_stage_2_and_split_from(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [
                {"title": "Fakten-Teil", "position": "PRO"},
                {"title": "Wert-Teil", "position": "CONTRA", "description": "moralisch"},
            ]},
        )
        assert resp.status_code == 201
        nodes = resp.json()
        assert len(nodes) == 2
        for n in nodes:
            assert n["stage_added"] == 2
            assert n["split_from_id"] == base["id"]
            assert n["topic_id"] == sample_topic["id"]
        assert nodes[1]["description"] == "moralisch"

    def test_split_inherits_base_parent_when_not_given(self, client, sample_user, sample_topic):
        opponent = self._base(client, sample_user, sample_topic)
        base = self._base(client, sample_user, sample_topic, parent_id=opponent["id"])
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "S1", "position": "PRO"}]},
        )
        assert resp.status_code == 201
        assert resp.json()[0]["parent_id"] == opponent["id"]

    def test_split_accepts_explicit_parent_id(self, client, sample_user, sample_topic):
        opponent_a = self._base(client, sample_user, sample_topic)
        opponent_b = self._base(client, sample_user, sample_topic)
        base = self._base(client, sample_user, sample_topic, parent_id=opponent_a["id"])
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [
                {"title": "answers A", "position": "PRO", "parent_id": opponent_a["id"]},
                {"title": "answers B", "position": "CONTRA", "parent_id": opponent_b["id"]},
            ]},
        )
        assert resp.status_code == 201
        parents = [n["parent_id"] for n in resp.json()]
        assert parents == [opponent_a["id"], opponent_b["id"]]

    def test_split_rejects_when_base_is_already_a_split(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        splits = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "S1", "position": "PRO"}]},
        ).json()
        # Try to split the split → 400
        resp = client.post(
            f"/api/arguments/{splits[0]['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "Nope", "position": "PRO"}]},
        )
        assert resp.status_code == 400

    def test_split_404_for_missing_base(self, client, sample_user):
        resp = client.post(
            f"/api/arguments/99999/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "x", "position": "PRO"}]},
        )
        assert resp.status_code == 404

    def test_split_requires_at_least_one_item(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": []},
        )
        assert resp.status_code == 422

    def test_split_rejects_invalid_position(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "bad", "position": "MAYBE"}]},
        )
        assert resp.status_code == 400

    def test_split_rejects_cross_topic_parent(self, client, sample_user, sample_topic):
        # Create a second topic via API
        other_topic = client.post(
            f"/api/topics/?user_id={sample_user['id']}",
            json={"title": "Other topic"},
        ).json()
        foreign = self._base(client, sample_user, other_topic)
        base = self._base(client, sample_user, sample_topic)
        resp = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "X", "position": "PRO", "parent_id": foreign["id"]}]},
        )
        assert resp.status_code == 400

    def test_zigzag_shows_splits_in_stage_2_and_hides_base_visually(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [
                {"title": "S1", "position": "PRO"},
                {"title": "S2", "position": "CONTRA"},
            ]},
        )
        stage1 = client.get(f"/api/topics/{sample_topic['id']}/zigzag?stage=1").json()
        assert [s["title"] for s in stage1["steps"]] == ["Base claim"]
        stage2 = client.get(f"/api/topics/{sample_topic['id']}/zigzag?stage=2").json()
        titles = [s["title"] for s in stage2["steps"]]
        assert "S1" in titles and "S2" in titles and "Base claim" in titles
        # Stage 3 frontend filters split-origin out; backend keeps them.
        split_nodes = [s for s in stage2["steps"] if s["split_from_id"] == base["id"]]
        assert len(split_nodes) == 2

    def test_connect_split_to_new_parent(self, client, sample_user, sample_topic):
        opponent_a = self._base(client, sample_user, sample_topic)
        opponent_b = self._base(client, sample_user, sample_topic)
        base = self._base(client, sample_user, sample_topic, parent_id=opponent_a["id"])
        split = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "S", "position": "PRO"}]},
        ).json()[0]
        assert split["parent_id"] == opponent_a["id"]
        resp = client.patch(f"/api/arguments/{split['id']}/connect", json={"parent_id": opponent_b["id"]})
        assert resp.status_code == 200
        assert resp.json()["parent_id"] == opponent_b["id"]

    def test_connect_split_unlink(self, client, sample_user, sample_topic):
        opponent = self._base(client, sample_user, sample_topic)
        base = self._base(client, sample_user, sample_topic, parent_id=opponent["id"])
        split = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "S", "position": "PRO"}]},
        ).json()[0]
        resp = client.patch(f"/api/arguments/{split['id']}/connect", json={"parent_id": None})
        assert resp.status_code == 200
        assert resp.json()["parent_id"] is None

    def test_connect_rejects_non_split_node(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        other = self._base(client, sample_user, sample_topic)
        resp = client.patch(f"/api/arguments/{base['id']}/connect", json={"parent_id": other["id"]})
        assert resp.status_code == 400

    def test_connect_rejects_self_parent(self, client, sample_user, sample_topic):
        base = self._base(client, sample_user, sample_topic)
        split = client.post(
            f"/api/arguments/{base['id']}/split?user_id={sample_user['id']}",
            json={"splits": [{"title": "S", "position": "PRO"}]},
        ).json()[0]
        resp = client.patch(f"/api/arguments/{split['id']}/connect", json={"parent_id": split["id"]})
        assert resp.status_code == 400


# ── Z.4b — Edge admissibility ─────────────────────────────────────────


class TestEdgeAdmissibility:
    """Marker on the parent→child connection (taxonomy §27)."""

    def _make_pair(self, client, user, topic):
        parent = client.post(
            f"/api/arguments/?user_id={user['id']}",
            json={"topic_id": topic["id"], "title": "Parent", "position": "PRO"},
        ).json()
        child = client.post(
            f"/api/arguments/?user_id={user['id']}",
            json={
                "topic_id": topic["id"],
                "parent_id": parent["id"],
                "title": "Child",
                "position": "CONTRA",
            },
        ).json()
        return parent, child

    def test_default_is_admissible(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        assert child["edge_admissibility"] == "ADMISSIBLE"

    def test_set_via_dedicated_endpoint(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        resp = client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": "OFF_TOPIC"},
        )
        assert resp.status_code == 200
        assert resp.json()["edge_admissibility"] == "OFF_TOPIC"

    def test_reset_via_dedicated_endpoint(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": "NON_SEQUITUR"},
        )
        resp = client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": None},
        )
        assert resp.status_code == 200
        assert resp.json()["edge_admissibility"] == "ADMISSIBLE"

    def test_set_via_generic_patch(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        resp = client.patch(
            f"/api/arguments/{child['id']}",
            json={"edge_admissibility": "SCOPE_VIOLATION"},
        )
        assert resp.status_code == 200
        assert resp.json()["edge_admissibility"] == "SCOPE_VIOLATION"

    def test_set_on_create(self, client, sample_user, sample_topic):
        parent = client.post(
            f"/api/arguments/?user_id={sample_user['id']}",
            json={"topic_id": sample_topic["id"], "title": "P", "position": "PRO"},
        ).json()
        resp = client.post(
            f"/api/arguments/?user_id={sample_user['id']}",
            json={
                "topic_id": sample_topic["id"],
                "parent_id": parent["id"],
                "title": "C",
                "position": "CONTRA",
                "edge_admissibility": "OFF_TOPIC",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["edge_admissibility"] == "OFF_TOPIC"

    def test_invalid_value_rejected(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        resp = client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": "BOGUS"},
        )
        assert resp.status_code == 400

    def test_root_node_rejected(self, client, sample_user, sample_topic):
        root = client.post(
            f"/api/arguments/?user_id={sample_user['id']}",
            json={"topic_id": sample_topic["id"], "title": "Root", "position": "PRO"},
        ).json()
        resp = client.patch(
            f"/api/arguments/{root['id']}/edge-admissibility",
            json={"admissibility": "OFF_TOPIC"},
        )
        assert resp.status_code == 400

    def test_emitted_by_zigzag(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": "OFF_TOPIC"},
        )
        resp = client.get(f"/api/topics/{sample_topic['id']}/zigzag")
        assert resp.status_code == 200
        steps = resp.json()["steps"]
        for s in steps:
            assert "edge_admissibility" in s
        marked = [s for s in steps if s["id"] == child["id"]]
        assert marked and marked[0]["edge_admissibility"] == "OFF_TOPIC"

    def test_emitted_by_tree(self, client, sample_user, sample_topic):
        _, child = self._make_pair(client, sample_user, sample_topic)
        client.patch(
            f"/api/arguments/{child['id']}/edge-admissibility",
            json={"admissibility": "SCOPE_VIOLATION"},
        )
        resp = client.get(f"/api/topics/{sample_topic['id']}/tree")
        assert resp.status_code == 200

        def find(nodes, nid):
            for n in nodes:
                if n["id"] == nid:
                    return n
                hit = find(n.get("children", []), nid)
                if hit:
                    return hit
            return None

        node = find(resp.json(), child["id"])
        assert node is not None
        assert node["edge_admissibility"] == "SCOPE_VIOLATION"

