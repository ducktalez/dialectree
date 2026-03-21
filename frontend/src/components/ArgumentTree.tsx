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
import type { ArgumentTreeNode } from "../types";
import { castVote, createArgument } from "../api";

const POSITION_COLORS: Record<string, string> = {
  PRO: "#4caf50",
  CONTRA: "#f44336",
  NEUTRAL: "#ff9800",
};

const H_SPACING = 300;
const V_SPACING = 150;

/**
 * Recursively flattens the argument tree into React Flow nodes + edges.
 * Layouts children horizontally under their parent.
 */
function treeToFlow(
  treeNodes: ArgumentTreeNode[],
  parentId: string | null,
  depth: number,
  xOffset: number
): { nodes: Node[]; edges: Edge[]; width: number } {
  const allNodes: Node[] = [];
  const allEdges: Edge[] = [];
  let currentX = xOffset;

  for (const tn of treeNodes) {
    const nodeId = `arg-${tn.id}`;

    // Recurse children first to know their total width
    const childResult = treeToFlow(tn.children, nodeId, depth + 1, currentX);
    allNodes.push(...childResult.nodes);
    allEdges.push(...childResult.edges);

    const myWidth = Math.max(childResult.width, 1);
    const myX = currentX + (myWidth * H_SPACING) / 2 - H_SPACING / 2;

    const metaParts: string[] = [];
    if (tn.tags.length > 0) metaParts.push(tn.tags.map(t => t.tag_name).join(", "));
    if (tn.labels.length > 0) metaParts.push(`⚠ ${tn.labels.join(", ")}`);
    if (tn.evidence_count > 0) metaParts.push(`📄${tn.evidence_count}`);
    if (tn.comment_count > 0) metaParts.push(`💬${tn.comment_count}`);
    const meta = metaParts.length > 0 ? `\n${metaParts.join(" · ")}` : "";
    const scoreSign = tn.vote_score > 0 ? "+" : "";

    allNodes.push({
      id: nodeId,
      position: { x: myX, y: depth * V_SPACING },
      data: {
        label: `${tn.title}\n${scoreSign}${tn.vote_score}${meta}`,
        argId: tn.id,
      },
      style: {
        background: POSITION_COLORS[tn.position] || "#ccc",
        color: "#fff",
        border: "1px solid #333",
        borderRadius: 8,
        padding: 10,
        fontSize: 12,
        width: 220,
        textAlign: "center" as const,
      },
    });

    if (parentId) {
      allEdges.push({
        id: `e-${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        type: "smoothstep",
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

interface Props {
  tree: ArgumentTreeNode[];
  topicId: number;
  onTreeChange: () => void;
}

export default function ArgumentTree({ tree, topicId, onTreeChange }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => treeToFlow(tree, null, 0, 0),
    [tree]
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
      </div>

      {/* Add argument form */}
      {showForm && (
        <form onSubmit={handleAddArgument} style={{ marginBottom: 12, padding: 8, border: "1px solid #ccc", borderRadius: 4 }}>
          <strong>{parentId ? `Reply to argument #${parentId}` : "New root argument"}</strong>
          <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
            <input
              value={argTitle}
              onChange={(e) => setArgTitle(e.target.value)}
              placeholder="Argument text…"
              style={{ flex: 1 }}
              autoFocus
            />
            <select value={argPosition} onChange={(e) => setArgPosition(e.target.value as "PRO" | "CONTRA" | "NEUTRAL")}>
              <option value="PRO">PRO</option>
              <option value="CONTRA">CONTRA</option>
              <option value="NEUTRAL">NEUTRAL</option>
            </select>
            <button type="submit">Add</button>
            <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
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
        >
          <Background />
          <Controls />
          <MiniMap
            nodeColor={(n) => (n.style?.background as string) || "#ccc"}
            zoomable
            pannable
          />
        </ReactFlow>
      </div>
    </div>
  );
}
