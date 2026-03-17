import { useCallback, useMemo } from "react";
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

    allNodes.push({
      id: nodeId,
      position: { x: myX, y: depth * V_SPACING },
      data: {
        label: `${tn.title}\n(${tn.position}, Score: ${tn.vote_score})`,
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
}

export default function ArgumentTree({ tree }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => treeToFlow(tree, null, 0, 0),
    [tree]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onInit = useCallback(() => {
    // future: fit view, etc.
  }, []);

  return (
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
  );
}

