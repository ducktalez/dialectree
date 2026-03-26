import { useCallback, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { ArgumentTreeNode, Position, StatementType, TagOnNode } from "../types";
import { castVote, createArgument } from "../api";

// ── Color utilities ───────────────────────────────────────────────────

/** Gradient from CONTRA red (0.0) → NEUTRAL grey (0.5) → PRO green (1.0) */
function positionScoreColor(score: number | null, position: Position): string {
  if (score == null) return POSITION_BG[position] || "#333";
  const clamped = Math.max(0, Math.min(1, score));
  if (clamped < 0.5) {
    const t = clamped / 0.5;
    return lerpColor("#d32f2f", "#757575", t);
  }
  const t = (clamped - 0.5) / 0.5;
  return lerpColor("#757575", "#388e3c", t);
}

function lerpColor(a: string, b: string, t: number): string {
  const parse = (c: string) => [
    parseInt(c.slice(1, 3), 16),
    parseInt(c.slice(3, 5), 16),
    parseInt(c.slice(5, 7), 16),
  ];
  const [r1, g1, b1] = parse(a);
  const [r2, g2, b2] = parse(b);
  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const bl = Math.round(b1 + (b2 - b1) * t);
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${bl.toString(16).padStart(2, "0")}`;
}

const POSITION_BG: Record<Position, string> = {
  PRO: "#388e3c",
  CONTRA: "#d32f2f",
  NEUTRAL: "#757575",
};

const STATEMENT_BADGE: Record<StatementType, { label: string; color: string }> = {
  POSITIVE: { label: "Ⓕ", color: "#42a5f5" },
  NORMATIVE: { label: "Ⓥ", color: "#ab47bc" },
  MIXED: { label: "Ⓜ", color: "#ffa726" },
  UNCLASSIFIED: { label: "", color: "#757575" },
};

const TAG_ORIGIN_ICON: Record<string, string> = {
  USER: "👤",
  MODERATOR: "🛡️",
  AI: "🤖",
};

// ── Tag grouping helper ───────────────────────────────────────────────

interface TagGroup {
  category: string;
  tags: TagOnNode[];
}

function groupTags(tags: TagOnNode[]): TagGroup[] {
  const groups: Record<string, TagOnNode[]> = {};
  for (const t of tags) {
    const cat = t.category || "OTHER";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(t);
  }
  return Object.entries(groups).map(([category, tags]) => ({ category, tags }));
}

// ── Node label builder ────────────────────────────────────────────────

function buildNodeLabel(tn: ArgumentTreeNode): string {
  const parts: string[] = [];

  // Title with statement type badge
  const stBadge = STATEMENT_BADGE[tn.statement_type];
  parts.push(stBadge?.label ? `${stBadge.label} ${tn.title}` : tn.title);

  // Vote score
  const sign = tn.vote_score > 0 ? "+" : "";
  parts.push(`${sign}${tn.vote_score}`);

  // Anatomy (compact summary)
  const anatomy: string[] = [];
  if (tn.claim) anatomy.push(`💬 ${tn.claim}`);
  if (tn.reason) anatomy.push(`📐 ${tn.reason}`);
  if (tn.example) anatomy.push(`📋 ${tn.example}`);
  if (tn.implication) anatomy.push(`➡ ${tn.implication}`);
  if (anatomy.length > 0) parts.push(anatomy.join("\n"));

  // Tags grouped by category with origin icon
  const tagGroups = groupTags(tn.tags);
  if (tagGroups.length > 0) {
    const tagStr = tagGroups
      .map((g) =>
        g.tags.map((t) => `${TAG_ORIGIN_ICON[t.origin] || ""}${t.tag_name}`).join(", ")
      )
      .join(" · ");
    parts.push(`🏷 ${tagStr}`);
  }

  // Labels
  if (tn.labels.length > 0) parts.push(`⚠ ${tn.labels.join(", ")}`);

  // Evidence, comments, conflicts
  const meta: string[] = [];
  if (tn.evidence_count > 0) meta.push(`📄${tn.evidence_count}`);
  if (tn.comment_count > 0) meta.push(`💬${tn.comment_count}`);
  if (tn.opens_conflict) meta.push(`→ ${tn.opens_conflict}`);
  if (meta.length > 0) parts.push(meta.join(" · "));

  return parts.join("\n");
}

// ── Layout ────────────────────────────────────────────────────────────

const H_SPACING = 300;
const V_SPACING = 180;

function treeToFlow(
  treeNodes: ArgumentTreeNode[],
  parentId: string | null,
  depth: number,
  xOffset: number,
  showHidden: boolean
): { nodes: Node[]; edges: Edge[]; width: number } {
  const allNodes: Node[] = [];
  const allEdges: Edge[] = [];
  let currentX = xOffset;

  for (const tn of treeNodes) {
    const isHidden = tn.visibility !== "VISIBLE";
    if (isHidden && !showHidden) continue;

    const nodeId = `arg-${tn.id}`;

    // Recurse children first
    const childResult = treeToFlow(tn.children, nodeId, depth + 1, currentX, showHidden);
    allNodes.push(...childResult.nodes);
    allEdges.push(...childResult.edges);

    const myWidth = Math.max(childResult.width, 1);
    const myX = currentX + (myWidth * H_SPACING) / 2 - H_SPACING / 2;

    const borderColor = positionScoreColor(tn.position_score, tn.position);

    allNodes.push({
      id: nodeId,
      position: { x: myX, y: depth * V_SPACING },
      data: {
        label: buildNodeLabel(tn),
        argId: tn.id,
        visibility: tn.visibility,
        hiddenReason: tn.hidden_reason,
      },
      style: {
        background: isHidden ? "#2a2a2a" : "#1c2128",
        color: "#c9d1d9",
        border: `3px solid ${borderColor}`,
        borderRadius: 8,
        padding: 10,
        fontSize: 11,
        width: 250,
        textAlign: "left" as const,
        whiteSpace: "pre-wrap" as const,
        opacity: isHidden ? 0.5 : 1,
        boxShadow: isHidden ? "none" : "0 2px 8px rgba(0,0,0,.3)",
      },
    });

    if (parentId) {
      allEdges.push({
        id: `e-${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        type: "smoothstep",
        style: {
          stroke: borderColor,
          strokeWidth: 2,
          opacity: isHidden ? 0.3 : 0.6,
        },
      });
    }

    currentX += myWidth * H_SPACING;
  }

  return {
    nodes: allNodes,
    edges: allEdges,
    width: Math.max((currentX - xOffset) / H_SPACING, treeNodes.length),
  };
}

// ── Component ─────────────────────────────────────────────────────────

interface Props {
  tree: ArgumentTreeNode[];
  topicId: number;
  onTreeChange: () => void;
}

export default function ArgumentTree({ tree, topicId, onTreeChange }: Props) {
  const [showHidden, setShowHidden] = useState(false);

  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => treeToFlow(tree, null, 0, 0, showHidden),
    [tree, showHidden]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  // Add-argument form state
  const [showForm, setShowForm] = useState(false);
  const [parentId, setParentId] = useState<number | null>(null);
  const [argTitle, setArgTitle] = useState("");
  const [argPosition, setArgPosition] = useState<"PRO" | "CONTRA" | "NEUTRAL">("PRO");

  const onInit = useCallback(() => {
    // future: fit view, etc.
  }, []);

  const handleVote = async (argId: number, value: 1 | -1) => {
    await castVote(argId, value);
    onTreeChange();
  };

  const handleAddArgument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!argTitle.trim()) return;
    await createArgument(topicId, argTitle.trim(), argPosition, parentId);
    setArgTitle("");
    setShowForm(false);
    setParentId(null);
    onTreeChange();
  };

  const openAddForm = (forParentId: number | null) => {
    setParentId(forParentId);
    setShowForm(true);
  };

  return (
    <div>
      {/* Controls above the tree */}
      <div style={{ marginBottom: 8, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <button onClick={() => openAddForm(null)}>+ Root Argument</button>

        {/* Per-node actions: add child */}
        {tree.length > 0 && (
          <select
            onChange={(e) => {
              const id = Number(e.target.value);
              if (id) openAddForm(id);
              e.target.value = "";
            }}
            defaultValue=""
            style={{ minWidth: 200 }}
          >
            <option value="" disabled>+ Child to…</option>
            {nodes
              .filter((n) => n.id.startsWith("arg-"))
              .map((n) => (
                <option key={n.id} value={(n.data as { argId: number }).argId}>
                  {String((n.data as { label: string }).label).split("\n")[0]}
                </option>
              ))}
          </select>
        )}

        {/* Inline vote buttons */}
        {tree.length > 0 && (
          <select
            onChange={async (e) => {
              const [id, val] = e.target.value.split(":");
              await handleVote(Number(id), Number(val) as 1 | -1);
              e.target.value = "";
            }}
            defaultValue=""
            style={{ minWidth: 180 }}
          >
            <option value="" disabled>Vote on…</option>
            {nodes
              .filter((n) => n.id.startsWith("arg-"))
              .flatMap((n) => {
                const argId = (n.data as { argId: number }).argId;
                const label = String((n.data as { label: string }).label).split("\n")[0];
                return [
                  <option key={`${argId}:1`} value={`${argId}:1`}>👍 {label}</option>,
                  <option key={`${argId}:-1`} value={`${argId}:-1`}>👎 {label}</option>,
                ];
              })}
          </select>
        )}

        {/* Show hidden toggle */}
        <label style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 13, color: "#8b949e" }}>
          <input
            type="checkbox"
            checked={showHidden}
            onChange={(e) => setShowHidden(e.target.checked)}
          />
          Show hidden arguments
        </label>
      </div>

      {/* Legend */}
      <div style={{ marginBottom: 8, display: "flex", gap: 12, flexWrap: "wrap", fontSize: 11, color: "#8b949e" }}>
        <span>🟢 PRO</span>
        <span>🔴 CONTRA</span>
        <span>⚪ NEUTRAL</span>
        <span title="Factual claim">Ⓕ Factual</span>
        <span title="Value judgment">Ⓥ Normative</span>
        <span>👤 User</span>
        <span>🛡️ Mod</span>
        <span>🤖 AI</span>
      </div>

      {/* Add argument form */}
      {showForm && (
        <form onSubmit={handleAddArgument} style={{ marginBottom: 12, padding: 8, border: "1px solid #30363d", borderRadius: 4, background: "#1c2128" }}>
          <strong style={{ color: "#e6edf3" }}>{parentId ? `Reply to argument #${parentId}` : "New root argument"}</strong>
          <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
            <input
              value={argTitle}
              onChange={(e) => setArgTitle(e.target.value)}
              placeholder="Argument text…"
              style={{ flex: 1, background: "#0d1117", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 4, padding: "4px 8px" }}
              autoFocus
            />
            <select
              value={argPosition}
              onChange={(e) => setArgPosition(e.target.value as "PRO" | "CONTRA" | "NEUTRAL")}
              style={{ background: "#0d1117", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 4 }}
            >
              <option value="PRO">PRO</option>
              <option value="CONTRA">CONTRA</option>
              <option value="NEUTRAL">NEUTRAL</option>
            </select>
            <button type="submit" style={{ background: "#1f6feb", color: "#fff", border: "none", borderRadius: 4, padding: "4px 12px", cursor: "pointer" }}>Add</button>
            <button type="button" onClick={() => setShowForm(false)} style={{ background: "#30363d", color: "#c9d1d9", border: "none", borderRadius: 4, padding: "4px 12px", cursor: "pointer" }}>Cancel</button>
          </div>
        </form>
      )}

      {/* React Flow tree */}
      <div style={{ width: "100%", height: "80vh" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={onInit}
          fitView
          style={{ background: "#0d1117" }}
        >
          <Background color="#30363d" gap={16} />
          <Controls />
          <MiniMap
            nodeColor={(n) => {
              const vis = (n.data as { visibility?: string })?.visibility;
              if (vis && vis !== "VISIBLE") return "#444";
              return (n.style?.borderColor as string) || "#666";
            }}
            style={{ background: "#161b22" }}
            zoomable
            pannable
          />
        </ReactFlow>
      </div>
    </div>
  );
}
