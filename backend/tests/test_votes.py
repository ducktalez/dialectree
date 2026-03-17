class TestVotes:
    def test_cast_vote(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": 1,
        })
        assert resp.status_code == 201
        assert resp.json()["value"] == 1

    def test_change_vote(self, client, sample_user, sample_argument):
        client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": 1,
        })
        resp = client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": -1,
        })
        assert resp.status_code == 201
        assert resp.json()["value"] == -1

    def test_invalid_vote_value(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": 5,
        })
        assert resp.status_code == 400

    def test_list_votes(self, client, sample_user, sample_argument):
        client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": 1,
        })
        resp = client.get(f"/api/votes/?argument_node_id={sample_argument['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_delete_vote(self, client, sample_user, sample_argument):
        vote = client.post(f"/api/votes/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "value": 1,
        }).json()
        resp = client.delete(f"/api/votes/{vote['id']}")
        assert resp.status_code == 204

