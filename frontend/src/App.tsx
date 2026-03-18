import { useEffect, useState } from "react";
import { fetchTopics, fetchTree, createTopic } from "./api";
import ArgumentTree from "./components/ArgumentTree";
import type { Topic, ArgumentTreeNode } from "./types";

export default function App() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [tree, setTree] = useState<ArgumentTreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const loadTopics = () => fetchTopics().then(setTopics);

  useEffect(() => {
    loadTopics();
  }, []);

  const reloadTree = () => {
    if (selectedTopic === null) return;
    setLoading(true);
    fetchTree(selectedTopic)
      .then(setTree)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    reloadTree();
  }, [selectedTopic]);

  const handleCreateTopic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const topic = await createTopic(newTitle.trim(), newDesc.trim());
    setNewTitle("");
    setNewDesc("");
    await loadTopics();
    setSelectedTopic(topic.id);
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: 20 }}>
      <h1>🌳 Dialectree</h1>
      <p>Structured argument trees for better discussions.</p>

      <h2>New Topic</h2>
      <form onSubmit={handleCreateTopic} style={{ marginBottom: 20 }}>
        <input
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="Topic question…"
          style={{ width: 300, marginRight: 8 }}
        />
        <input
          value={newDesc}
          onChange={(e) => setNewDesc(e.target.value)}
          placeholder="Description (optional)"
          style={{ width: 300, marginRight: 8 }}
        />
        <button type="submit">Create</button>
      </form>

      <h2>Topics</h2>
      {topics.length === 0 && (
        <p>
          No topics found. Start the backend and load seed data:
          <code> python -m app.seed</code>
        </p>
      )}
      <ul>
        {topics.map((t) => (
          <li key={t.id}>
            <button
              onClick={() => setSelectedTopic(t.id)}
              style={{
                fontWeight: selectedTopic === t.id ? "bold" : "normal",
                cursor: "pointer",
                background: "none",
                border: "none",
                textDecoration: "underline",
                fontSize: 16,
                color: selectedTopic === t.id ? "#333" : "#1976d2",
              }}
            >
              {t.title}
            </button>
          </li>
        ))}
      </ul>

      {loading && <p>Loading argument tree…</p>}

      {!loading && selectedTopic && (
        <ArgumentTree
          tree={tree}
          topicId={selectedTopic}
          onTreeChange={reloadTree}
        />
      )}

      {!loading && selectedTopic && tree.length === 0 && (
        <p>No arguments found for this topic. Add one above!</p>
      )}
    </div>
  );
}
