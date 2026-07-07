export interface User {
  id: string;
  email: string;
  name: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  icon: string;
  user_id: string | null;
}

export type TaskStatus = "todo" | "in_progress" | "review" | "done";
export type TaskType = "idea" | "goal" | "epic" | "feature" | "task" | "bug";

export const TASK_STATUSES: TaskStatus[] = ["todo", "in_progress", "review", "done"];
export const TASK_TYPES: TaskType[] = ["idea", "goal", "epic", "feature", "task", "bug"];

export type RelationshipName =
  | "blocks"
  | "blocked_by"
  | "parent_of"
  | "child_of"
  | "related_to";

export const RELATIONSHIP_NAMES: RelationshipName[] = [
  "blocks",
  "blocked_by",
  "parent_of",
  "child_of",
  "related_to",
];

export interface TaskRef {
  id: string;
  title: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  deadline: string | null;
  status: TaskStatus;
  type: TaskType;
  user_id: string | null;
  created_at: string | null;
  updated_at: string | null;
  relationships?: Record<RelationshipName, TaskRef[]>;
}

export interface GraphNode {
  id: string;
  label: string;
  icon: string;
  color: string;
  type: string;
  status: string;
}

export interface GraphEdge {
  source: number;
  target: number;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  groups: { leaves: number[] }[];
  constraints: unknown[];
}

export interface CalendarData {
  year: number;
  month: number;
  tasks: Task[];
}
