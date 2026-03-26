export interface Topic {
  id: number;
  title: string;
  description: string | null;
  transcript_yaml: string | null;
  created_by: number;
  created_at: string;
}

export interface TagOnNode {
  tag_id: number;
  tag_name: string;
  category: string | null;
  moral_foundation: string | null;
  origin: string;
}

export type Position = "PRO" | "CONTRA" | "NEUTRAL";
export type StatementType = "POSITIVE" | "NORMATIVE" | "MIXED" | "UNCLASSIFIED";
export type Visibility = "VISIBLE" | "VOTED_DOWN" | "MOD_HIDDEN" | "MOVED" | "MERGED" | "SUPERSEDED" | "PENDING_REVIEW";

export interface ArgumentTreeNode {
  id: number;
  title: string;
  description: string | null;
  position: Position;
  position_score: number | null;
  statement_type: StatementType;
  visibility: Visibility;
  hidden_reason: string | null;
  parent_id: number | null;
  argument_group_id: number | null;
  // Argument anatomy
  claim: string | null;
  reason: string | null;
  example: string | null;
  implication: string | null;
  // Zigzag fields
  conflict_zone: string | null;
  edge_type: string | null;
  is_edge_attack: boolean;
  opens_conflict: string | null;
  created_by: number;
  vote_score: number;
  tags: TagOnNode[];
  labels: string[];
  evidence_count: number;
  comment_count: number;
  children: ArgumentTreeNode[];
}

