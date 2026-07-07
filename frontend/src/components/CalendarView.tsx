import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { CalendarData, Task } from "../types";
import { colorToHex } from "../colors";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const STATUS_COLOR: Record<string, string> = {
  todo: "gray-400",
  in_progress: "blue-500",
  review: "yellow-500",
  done: "green-500",
};

export default function CalendarView({
  projectId,
  onSelectTask,
}: {
  projectId: string;
  onSelectTask: (taskId: string) => void;
}) {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [data, setData] = useState<CalendarData | null>(null);

  useEffect(() => {
    void api.calendar(projectId, year, month).then(setData);
  }, [projectId, year, month]);

  const previous = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const next = () => {
    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  const daysInMonth = new Date(year, month, 0).getDate();
  // Weeks start on Monday
  const firstWeekday = (new Date(year, month - 1, 1).getDay() + 6) % 7;

  const tasksByDay = new Map<number, Task[]>();
  for (const task of data?.tasks ?? []) {
    if (!task.deadline) continue;
    const day = Number(task.deadline.slice(8, 10));
    tasksByDay.set(day, [...(tasksByDay.get(day) ?? []), task]);
  }

  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-4 flex items-center justify-between">
        <button onClick={previous} className="rounded px-3 py-1 text-gray-600 hover:bg-gray-100">
          ← Previous
        </button>
        <h2 className="text-lg font-semibold text-gray-800">
          {MONTHS[month - 1]} {year}
        </h2>
        <button onClick={next} className="rounded px-3 py-1 text-gray-600 hover:bg-gray-100">
          Next →
        </button>
      </div>

      <div className="grid grid-cols-7 gap-px overflow-hidden rounded-lg border border-gray-200 bg-gray-200 text-sm">
        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day) => (
          <div key={day} className="bg-gray-50 px-2 py-1 text-center font-medium text-gray-500">
            {day}
          </div>
        ))}

        {Array.from({ length: firstWeekday }).map((_, i) => (
          <div key={`empty-${i}`} className="min-h-24 bg-white" />
        ))}

        {Array.from({ length: daysInMonth }).map((_, i) => {
          const day = i + 1;
          return (
            <div key={day} className="min-h-24 bg-white p-1">
              <div className="mb-1 text-xs text-gray-400">{day}</div>
              {(tasksByDay.get(day) ?? []).map((task) => (
                <button
                  key={task.id}
                  onClick={() => onSelectTask(task.id)}
                  className="mb-1 block w-full truncate rounded px-1.5 py-0.5 text-left text-xs text-white"
                  style={{ backgroundColor: colorToHex(STATUS_COLOR[task.status]) }}
                  title={task.title}
                >
                  {task.title}
                </button>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
