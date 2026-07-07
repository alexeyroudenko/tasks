// Maps backend color tokens (Tailwind palette names) to hex values for SVG
const PALETTE: Record<string, string> = {
  "gray-400": "#9ca3af",
  "gray-500": "#6b7280",
  "blue-500": "#3b82f6",
  "yellow-500": "#eab308",
  "green-500": "#22c55e",
  "purple-500": "#a855f7",
  "pink-500": "#ec4899",
  "red-500": "#ef4444",
  "red-600": "#dc2626",
};

export function colorToHex(token: string): string {
  return PALETTE[token] ?? "#6b7280";
}

export const STATUS_LABELS: Record<string, string> = {
  todo: "To Do",
  in_progress: "In Progress",
  review: "Review",
  done: "Done",
};
