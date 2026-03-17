export interface Topic {
  id: number;
  title: string;
  description: string | null;
  created_by: number;
  created_at: string;
}

export interface ArgumentTreeNode {
  id: number;
  title: string;
  description: string | null;
  position: "PRO" | "CONTRA" | "NEUTRAL";
  parent_id: number | null;
  vote_score: number;
  children: ArgumentTreeNode[];
}

