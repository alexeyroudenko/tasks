import { describe, expect, it } from "vitest";
import { resolveDark, THEMES } from "./theme";

describe("resolveDark", () => {
  it("returns the explicit choice regardless of system preference", () => {
    expect(resolveDark("dark", false)).toBe(true);
    expect(resolveDark("dark", true)).toBe(true);
    expect(resolveDark("light", true)).toBe(false);
    expect(resolveDark("light", false)).toBe(false);
  });

  it("follows the system preference in system mode", () => {
    expect(resolveDark("system", true)).toBe(true);
    expect(resolveDark("system", false)).toBe(false);
  });
});

describe("THEMES", () => {
  it("offers light, dark and system", () => {
    expect(THEMES).toEqual(["light", "dark", "system"]);
  });
});
