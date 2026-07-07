import { describe, expect, it } from "vitest";
import { colorToHex, STATUS_LABELS } from "./colors";

describe("colorToHex", () => {
  it("maps known palette tokens to hex", () => {
    expect(colorToHex("blue-500")).toBe("#3b82f6");
    expect(colorToHex("green-500")).toBe("#22c55e");
  });

  it("falls back to gray for unknown tokens", () => {
    expect(colorToHex("nonexistent")).toBe("#6b7280");
  });
});

describe("STATUS_LABELS", () => {
  it("covers all task statuses", () => {
    expect(Object.keys(STATUS_LABELS)).toEqual([
      "todo",
      "in_progress",
      "review",
      "done",
    ]);
  });
});
