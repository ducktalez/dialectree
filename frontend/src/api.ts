import type { Topic, ArgumentTreeNode } from "./types";

const BASE = "/api";

export async function fetchTopics(): Promise<Topic[]> {
  const res = await fetch(`${BASE}/topics/`);
  return res.json();
}

export async function fetchTopic(id: number): Promise<Topic> {
  const res = await fetch(`${BASE}/topics/${id}`);
  return res.json();
}

export async function fetchTree(topicId: number): Promise<ArgumentTreeNode[]> {
  const res = await fetch(`${BASE}/topics/${topicId}/tree`);
  return res.json();
}

export async function createTopic(
  title: string,
  description: string,
  userId: number = 1
): Promise<Topic> {
  const res = await fetch(`${BASE}/topics/?user_id=${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description: description || null }),
  });
  return res.json();
}

export async function createArgument(
  topicId: number,
  title: string,
  position: "PRO" | "CONTRA" | "NEUTRAL",
  parentId: number | null = null,
  userId: number = 1
): Promise<unknown> {
  const res = await fetch(`${BASE}/arguments/?user_id=${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic_id: topicId,
      parent_id: parentId,
      title,
      position,
    }),
  });
  return res.json();
}

export async function castVote(
  argumentNodeId: number,
  value: 1 | -1,
  userId: number = 1
): Promise<unknown> {
  const res = await fetch(`${BASE}/votes/?user_id=${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ argument_node_id: argumentNodeId, value }),
  });
  return res.json();
}

