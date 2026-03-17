class TestComments:
    def test_create_comment(self, client, sample_user, sample_argument):
        resp = client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"],
            "text": "This is a test comment.",
        })
        assert resp.status_code == 201
        assert resp.json()["text"] == "This is a test comment."

    def test_list_comments(self, client, sample_user, sample_argument):
        client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "text": "Comment 1",
        })
        client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "text": "Comment 2",
        })
        resp = client.get(f"/api/comments/?argument_node_id={sample_argument['id']}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_comment(self, client, sample_user, sample_argument):
        comment = client.post(f"/api/comments/?user_id={sample_user['id']}", json={
            "argument_node_id": sample_argument["id"], "text": "To delete",
        }).json()
        resp = client.delete(f"/api/comments/{comment['id']}")
        assert resp.status_code == 204

    def test_delete_comment_not_found(self, client):
        resp = client.delete("/api/comments/9999")
        assert resp.status_code == 404

