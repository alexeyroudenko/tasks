import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { GraphData, GraphEdge, GraphNode } from "../types";
import { colorToHex } from "../colors";
import { ICON_PATHS } from "../icons";

const NODE_WIDTH = 160;
const NODE_HEIGHT = 60;
const NODE_RADIUS = 6;

interface SimNode extends GraphNode, d3.SimulationNodeDatum {}
interface SimEdge extends d3.SimulationLinkDatum<SimNode> {
  label: string;
}

export default function GraphView({
  data,
  onSelectTask,
}: {
  data: GraphData;
  onSelectTask: (taskId: string) => void;
}) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement) return;

    const { width, height } = svgElement.getBoundingClientRect();

    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();

    // Arrowhead marker
    svg
      .append("defs")
      .append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 10)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#9ca3af");

    const container = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 3])
      .on("zoom", (event) => container.attr("transform", event.transform));

    svg.call(zoom);

    const nodes: SimNode[] = data.nodes.map((n) => ({ ...n }));
    const edges: SimEdge[] = data.edges.map((e: GraphEdge) => ({
      source: e.source,
      target: e.target,
      label: e.label,
    }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3.forceLink<SimNode, SimEdge>(edges).distance(220).strength(0.4),
      )
      .force("charge", d3.forceManyBody().strength(-600))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide(Math.max(NODE_WIDTH, NODE_HEIGHT) / 1.6));

    const edgeLines = container
      .selectAll<SVGLineElement, SimEdge>(".link")
      .data(edges)
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("stroke", "#9ca3af")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#arrow)");

    const edgeLabels = container
      .selectAll<SVGTextElement, SimEdge>(".link-label")
      .data(edges)
      .enter()
      .append("text")
      .attr("class", "link-label")
      .attr("font-size", 11)
      .attr("fill", "#6b7280")
      .attr("text-anchor", "middle")
      .text((d) => d.label);

    const nodeGroups = container
      .selectAll<SVGGElement, SimNode>(".node")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("cursor", "pointer")
      .on("click", (_event, d) => onSelectTask(d.id))
      .call(
        d3
          .drag<SVGGElement, SimNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }),
      );

    nodeGroups
      .append("rect")
      .attr("width", NODE_WIDTH)
      .attr("height", NODE_HEIGHT)
      .attr("rx", NODE_RADIUS)
      .attr("fill", "#ffffff")
      .attr("stroke", (d) => colorToHex(d.status))
      .attr("stroke-width", 2);

    nodeGroups
      .append("text")
      .attr("x", 10)
      .attr("y", 22)
      .attr("font-size", 12)
      .attr("font-weight", 600)
      .attr("fill", "#111827")
      .text((d) =>
        d.label.length > 22 ? `${d.label.slice(0, 22)}…` : d.label,
      );

    nodeGroups
      .append("path")
      .attr("d", (d) => ICON_PATHS[d.icon] ?? "")
      .attr("transform", `translate(8, ${NODE_HEIGHT - 26}) scale(0.7)`)
      .attr("fill", "none")
      .attr("stroke", (d) => colorToHex(d.color))
      .attr("stroke-width", 2)
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round");

    nodeGroups
      .append("text")
      .attr("x", 30)
      .attr("y", NODE_HEIGHT - 12)
      .attr("font-size", 11)
      .attr("fill", (d) => colorToHex(d.color))
      .text((d) => d.type);

    simulation.on("tick", () => {
      nodeGroups.attr(
        "transform",
        (d) => `translate(${(d.x ?? 0) - NODE_WIDTH / 2}, ${(d.y ?? 0) - NODE_HEIGHT / 2})`,
      );

      edgeLines
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0);

      edgeLabels
        .attr("x", (d) => (((d.source as SimNode).x ?? 0) + ((d.target as SimNode).x ?? 0)) / 2)
        .attr("y", (d) => (((d.source as SimNode).y ?? 0) + ((d.target as SimNode).y ?? 0)) / 2 - 6);
    });

    return () => {
      simulation.stop();
    };
  }, [data, onSelectTask]);

  return <svg ref={svgRef} className="h-full w-full bg-gray-50" />;
}
