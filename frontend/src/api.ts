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

