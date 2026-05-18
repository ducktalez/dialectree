class TestDefinitionForks:
    def test_create_definition_fork(self, client, sample_argument):
        resp = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "racism",
            "definition_variant": "Systemic racism (institutional power structures)",
            "description": "Racism as a system, not individual prejudice.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["term"] == "racism"
        assert data["definition_variant"] == "Systemic racism (institutional power structures)"

    def test_create_definition_fork_minimal(self, client, sample_argument):
        resp = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "freedom",
            "definition_variant": "Negative freedom (absence of constraint)",
        })
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_list_definition_forks(self, client, sample_argument):
        client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "racism",
            "definition_variant": "Variant A",
        })
        client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "racism",
            "definition_variant": "Variant B",
        })
        resp = client.get(f"/api/definition-forks/?argument_node_id={sample_argument['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_all_definition_forks(self, client, sample_argument):
        client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "freedom",
            "definition_variant": "Variant A",
        })
        resp = client.get("/api/definition-forks/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_definition_fork(self, client, sample_argument):
        fork = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "equality",
            "definition_variant": "Equality of opportunity",
        }).json()
        resp = client.get(f"/api/definition-forks/{fork['id']}")
        assert resp.status_code == 200
        assert resp.json()["term"] == "equality"

    def test_get_definition_fork_not_found(self, client):
        resp = client.get("/api/definition-forks/9999")
        assert resp.status_code == 404

    def test_delete_definition_fork(self, client, sample_argument):
        fork = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "justice",
            "definition_variant": "Retributive justice",
        }).json()
        resp = client.delete(f"/api/definition-forks/{fork['id']}")
        assert resp.status_code == 204
        resp = client.get(f"/api/definition-forks/{fork['id']}")
        assert resp.status_code == 404

    def test_delete_definition_fork_not_found(self, client):
        resp = client.delete("/api/definition-forks/9999")
        assert resp.status_code == 404

    def test_cascade_delete_with_argument(self, client, sample_user, sample_topic):
        """Deleting an argument should also delete its definition forks."""
        arg = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"],
            "title": "Temp argument",
            "position": "PRO",
        }).json()
        fork = client.post("/api/definition-forks/", json={
            "argument_node_id": arg["id"],
            "term": "temp",
            "definition_variant": "Temp variant",
        }).json()
        client.delete(f"/api/arguments/{arg['id']}")
        resp = client.get(f"/api/definition-forks/{fork['id']}")
        assert resp.status_code == 404

    # ── new endpoints (PATCH + topic-wide listing) ──────────────────────

    def test_create_rejects_unknown_argument(self, client):
        resp = client.post("/api/definition-forks/", json={
            "argument_node_id": 9999,
            "term": "ghost",
            "definition_variant": "Variant",
        })
        assert resp.status_code == 404

    def test_list_by_topic(self, client, sample_user, sample_topic, sample_argument):
        arg2 = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": sample_topic["id"], "title": "Arg 2", "position": "CONTRA",
        }).json()
        topic2 = client.post(f"/api/topics/?user_id={sample_user['id']}", json={
            "title": "Other topic",
        }).json()
        arg_other = client.post(f"/api/arguments/?user_id={sample_user['id']}", json={
            "topic_id": topic2["id"], "title": "Arg other", "position": "PRO",
        }).json()
        client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"], "term": "x", "definition_variant": "A",
        })
        client.post("/api/definition-forks/", json={
            "argument_node_id": arg2["id"], "term": "x", "definition_variant": "B",
        })
        client.post("/api/definition-forks/", json={
            "argument_node_id": arg_other["id"], "term": "x", "definition_variant": "C",
        })
        resp = client.get(f"/api/definition-forks/?topic_id={sample_topic['id']}")
        assert resp.status_code == 200
        variants = sorted(f["definition_variant"] for f in resp.json())
        assert variants == ["A", "B"]

    def test_patch_definition_fork(self, client, sample_argument):
        fork = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "racism",
            "definition_variant": "old",
            "description": "old desc",
        }).json()
        resp = client.patch(f"/api/definition-forks/{fork['id']}", json={
            "definition_variant": "new variant", "description": None,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["term"] == "racism"
        assert body["definition_variant"] == "new variant"
        assert body["description"] is None

    def test_patch_rejects_empty_term(self, client, sample_argument):
        fork = client.post("/api/definition-forks/", json={
            "argument_node_id": sample_argument["id"],
            "term": "x", "definition_variant": "y",
        }).json()
        resp = client.patch(f"/api/definition-forks/{fork['id']}", json={"term": "  "})
        assert resp.status_code == 400

    def test_patch_not_found(self, client):
        resp = client.patch("/api/definition-forks/9999", json={"term": "x"})
        assert resp.status_code == 404
