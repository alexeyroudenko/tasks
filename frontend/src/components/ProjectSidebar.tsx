import { useState } from "react";
import { api } from "../api/client";
import type { Project } from "../types";
import { TypeIcon } from "../icons";

export default function ProjectSidebar({
  projects,
  selectedId,
  onSelect,
  onChanged,
}: {
  projects: Project[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onChanged: () => void;
}) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");

  const create = async () => {
    if (!name.trim()) return;
    const project = await api.createProject({ name: name.trim() });
    setName("");
    setCreating(false);
    onChanged();
    onSelect(project.id);
  };

  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h1 className="text-lg font-bold text-red-600">Tasks</h1>
        <button
          onClick={() => setCreating(!creating)}
          className="rounded bg-gray-100 px-2 py-1 text-sm text-gray-600 hover:bg-gray-200"
        >
          + New
        </button>
      </div>

      {creating && (
        <div className="border-b border-gray-200 p-3">
          <input
            autoFocus
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void create()}
            placeholder="Project name"
            className="mb-2 w-full rounded border border-gray-300 px-2 py-1.5 text-sm"
          />
          <button
            onClick={() => void create()}
            className="w-full rounded bg-blue-600 py-1.5 text-sm text-white hover:bg-blue-700"
          >
            Create project
          </button>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto p-2">
        {projects.map((project) => (
          <button
            key={project.id}
            onClick={() => onSelect(project.id)}
            className={`mb-1 flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm ${
              project.id === selectedId
                ? "bg-blue-50 font-medium text-blue-700"
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <TypeIcon icon={project.icon} className="h-4 w-4 shrink-0" />
            <span className="truncate">{project.name}</span>
          </button>
        ))}
        {projects.length === 0 && (
          <p className="px-3 py-2 text-sm text-gray-400">No projects yet</p>
        )}
      </nav>
    </aside>
  );
}
