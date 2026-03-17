import { useEffect, useState } from "react";
import { fetchTopics, fetchTree } from "./api";
import ArgumentTree from "./components/ArgumentTree";
import type { Topic, ArgumentTreeNode } from "./types";

export default function App() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [tree, setTree] = useState<ArgumentTreeNode[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTopics().then(setTopics);
  }, []);

  useEffect(() => {
    if (selectedTopic === null) return;
    setLoading(true);
    fetchTree(selectedTopic)
      .then(setTree)
      .finally(() => setLoading(false));
  }, [selectedTopic]);

  return (
    <div style={{ fontFamily: "sans-serif", padding: 20 }}>
      <h1>🌳 Dialectree</h1>
      <p>Structured argument trees for better discussions.</p>

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

      {!loading && tree.length > 0 && <ArgumentTree tree={tree} />}

      {!loading && selectedTopic && tree.length === 0 && (
        <p>No arguments found for this topic.</p>
      )}
    </div>
  );
}
