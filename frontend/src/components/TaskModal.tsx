import { useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  RelationshipName,
  Task,
  TaskRef,
  User,
} from "../types";
import { RELATIONSHIP_NAMES, TASK_STATUSES, TASK_TYPES } from "../types";
import { STATUS_LABELS } from "../colors";

const RELATIONSHIP_LABELS: Record<RelationshipName, string> = {
  blocks: "Blocks",
  blocked_by: "Blocked by",
  parent_of: "Parent of",
  child_of: "Child of",
  related_to: "Related to",
};

const inputClass =
  "w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100";
const selectClass =
  "w-full rounded border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100";
const labelClass =
  "mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300";

export default function TaskModal({
  projectId,
  taskId,
  users,
  allTasks,
  onClose,
  onChanged,
}: {
  projectId: string;
  taskId: string | null; // null means "create a new task"
  users: User[];
  allTasks: TaskRef[];
  onClose: () => void;
  onChanged: () => void;
}) {
  const [task, setTask] = useState<Task | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [deadline, setDeadline] = useState("");
  const [status, setStatus] = useState("todo");
  const [type, setType] = useState("task");
  const [userId, setUserId] = useState("");
  const [newRelType, setNewRelType] = useState<RelationshipName>("related_to");
  const [newRelTarget, setNewRelTarget] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    if (!taskId) return;
    const data = await api.task(projectId, taskId);
    setTask(data);
    setTitle(data.title ?? "");
    setDescription(data.description ?? "");
    setDeadline(data.deadline ?? "");
    setStatus(data.status);
    setType(data.type);
    setUserId(data.user_id ?? "");
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, taskId]);

  const save = async () => {
    const payload = {
      title,
      description: description || null,
      deadline: deadline || null,
      status,
      type,
      user_id: userId || null,
    } as Partial<Task>;

    if (taskId) {
      await api.updateTask(projectId, taskId, payload);
    } else {
      await api.createTask(projectId, payload);
    }

    setNotice("Task saved");
    onChanged();
    if (taskId) void load();
    else onClose();
  };

  const remove = async () => {
    if (!taskId) return;
    if (!window.confirm("Delete this task?")) return;
    await api.deleteTask(projectId, taskId);
    onChanged();
    onClose();
  };

  const addRelationship = async () => {
    if (!taskId || !newRelTarget) return;
    await api.createRelationship(projectId, {
      from_id: taskId,
      type: newRelType,
      to_id: newRelTarget,
    });
    setNewRelTarget("");
    onChanged();
    void load();
  };

  const removeRelationship = async (name: RelationshipName, ref: TaskRef) => {
    if (!taskId) return;
    await api.deleteRelationship(projectId, {
      from_id: taskId,
      type: name,
      to_id: ref.id,
    });
    onChanged();
    void load();
  };

  const otherTasks = allTasks.filter((t) => t.id !== taskId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 dark:bg-black/60">
      <div className="max-h-full w-full max-w-lg overflow-y-auto rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
            {taskId ? "Edit task" : "New task"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {notice && (
          <div className="mb-3 rounded bg-green-50 px-3 py-2 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
            {notice}
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className={labelClass}>Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label className={labelClass}>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className={inputClass}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className={selectClass}
              >
                {TASK_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {STATUS_LABELS[s]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className={selectClass}
              >
                {TASK_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Deadline</label>
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className={selectClass}
              />
            </div>
            <div>
              <label className={labelClass}>Assignee</label>
              <select
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className={selectClass}
              >
                <option value="">—</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {taskId && task?.relationships && (
          <div className="mt-5 border-t border-gray-200 pt-4 dark:border-gray-700">
            <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              Relationships
            </h3>

            <ul className="space-y-1">
              {RELATIONSHIP_NAMES.flatMap((name) =>
                (task.relationships?.[name] ?? []).map((ref) => (
                  <li
                    key={`${name}-${ref.id}`}
                    className="flex items-center justify-between rounded bg-gray-50 px-3 py-1.5 text-sm dark:bg-gray-700"
                  >
                    <span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {RELATIONSHIP_LABELS[name]}
                      </span>{" "}
                      <span className="font-medium text-gray-800 dark:text-gray-100">
                        {ref.title}
                      </span>
                    </span>
                    <button
                      onClick={() => void removeRelationship(name, ref)}
                      className="text-gray-400 hover:text-red-500"
                      aria-label="Remove relationship"
                    >
                      ✕
                    </button>
                  </li>
                )),
              )}
            </ul>

            <div className="mt-2 flex gap-2">
              <select
                value={newRelType}
                onChange={(e) => setNewRelType(e.target.value as RelationshipName)}
                className="rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
              >
                {RELATIONSHIP_NAMES.map((name) => (
                  <option key={name} value={name}>
                    {RELATIONSHIP_LABELS[name]}
                  </option>
                ))}
              </select>
              <select
                value={newRelTarget}
                onChange={(e) => setNewRelTarget(e.target.value)}
                className="flex-1 rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
              >
                <option value="">Select task…</option>
                {otherTasks.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title}
                  </option>
                ))}
              </select>
              <button
                onClick={() => void addRelationship()}
                disabled={!newRelTarget}
                className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                Add
              </button>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-between">
          {taskId ? (
            <button
              onClick={() => void remove()}
              className="rounded px-3 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
            >
              Delete
            </button>
          ) : (
            <span />
          )}
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="rounded px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              onClick={() => void save()}
              disabled={!title}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
