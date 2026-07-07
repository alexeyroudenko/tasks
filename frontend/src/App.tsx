import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import type { GraphData, Project, TaskRef, User } from "./types";
import ProjectSidebar from "./components/ProjectSidebar";
import GraphView from "./components/GraphView";
import CalendarView from "./components/CalendarView";
import TaskModal from "./components/TaskModal";

type View = "graph" | "calendar";

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [view, setView] = useState<View>("graph");
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [taskRefs, setTaskRefs] = useState<TaskRef[]>([]);
  const [modal, setModal] = useState<{ open: boolean; taskId: string | null }>({
    open: false,
    taskId: null,
  });

  const loadProjects = useCallback(async () => {
    const data = await api.projects();
    setProjects(data);
    setProjectId((current) => current ?? data[0]?.id ?? null);
  }, []);

  const loadGraph = useCallback(async () => {
    if (!projectId) return;
    const [graphData, tasks] = await Promise.all([
      api.graph(projectId),
      api.tasks(projectId),
    ]);
    setGraph(graphData);
    setTaskRefs(tasks.map((t) => ({ id: t.id, title: t.title })));
  }, [projectId]);

  useEffect(() => {
    void loadProjects();
    void api.users().then(setUsers);
  }, [loadProjects]);

  useEffect(() => {
    void loadGraph();
  }, [loadGraph]);

  const openTask = useCallback(
    (taskId: string) => setModal({ open: true, taskId }),
    [],
  );

  return (
    <div className="flex h-screen bg-gray-50">
      <ProjectSidebar
        projects={projects}
        selectedId={projectId}
        onSelect={setProjectId}
        onChanged={() => void loadProjects()}
      />

      <main className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-2">
          <div className="flex gap-1">
            {(["graph", "calendar"] as View[]).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded px-3 py-1.5 text-sm capitalize ${
                  view === v
                    ? "bg-blue-600 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {v}
              </button>
            ))}
          </div>

          <button
            onClick={() => setModal({ open: true, taskId: null })}
            disabled={!projectId}
            className="rounded bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            + New task
          </button>
        </header>

        <div className="flex-1 overflow-hidden">
          {!projectId ? (
            <div className="flex h-full items-center justify-center text-gray-400">
              Create a project to get started
            </div>
          ) : view === "graph" ? (
            graph && <GraphView data={graph} onSelectTask={openTask} />
          ) : (
            <CalendarView projectId={projectId} onSelectTask={openTask} />
          )}
        </div>
      </main>

      {modal.open && projectId && (
        <TaskModal
          projectId={projectId}
          taskId={modal.taskId}
          users={users}
          allTasks={taskRefs}
          onClose={() => setModal({ open: false, taskId: null })}
          onChanged={() => void loadGraph()}
        />
      )}
    </div>
  );
}
