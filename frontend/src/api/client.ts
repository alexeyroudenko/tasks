import type {
  CalendarData,
  GraphData,
  Project,
  Task,
  User,
} from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  users: () => request<User[]>("/api/users"),

  projects: () => request<Project[]>("/api/projects"),
  createProject: (data: { name: string; description?: string }) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify(data) }),
  deleteProject: (id: string) =>
    request<void>(`/api/projects/${id}`, { method: "DELETE" }),

  tasks: (projectId: string) => request<Task[]>(`/api/projects/${projectId}/tasks`),
  task: (projectId: string, taskId: string) =>
    request<Task>(`/api/projects/${projectId}/tasks/${taskId}`),
  createTask: (projectId: string, data: Partial<Task>) =>
    request<Task>(`/api/projects/${projectId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateTask: (projectId: string, taskId: string, data: Partial<Task>) =>
    request<Task>(`/api/projects/${projectId}/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deleteTask: (projectId: string, taskId: string) =>
    request<void>(`/api/projects/${projectId}/tasks/${taskId}`, { method: "DELETE" }),

  graph: (projectId: string) => request<GraphData>(`/api/projects/${projectId}/graph`),

  createRelationship: (projectId: string, data: { from_id: string; type: string; to_id: string }) =>
    request<void>(`/api/projects/${projectId}/relationships`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteRelationship: (projectId: string, data: { from_id: string; type: string; to_id: string }) =>
    request<void>(`/api/projects/${projectId}/relationships`, {
      method: "DELETE",
      body: JSON.stringify(data),
    }),

  calendar: (projectId: string, year: number, month: number) =>
    request<CalendarData>(`/api/projects/${projectId}/calendar?year=${year}&month=${month}`),
};
