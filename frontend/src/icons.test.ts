import { describe, expect, it } from "vitest";
import { ICON_PATHS } from "./icons";

describe("ICON_PATHS", () => {
  it("has an icon for every task type emitted by the backend", () => {
    const expected = [
      "light-bulb",
      "flag",
      "collection",
      "puzzle",
      "clipboard-list",
      "exclamation-circle",
    ];

    for (const name of expected) {
      expect(ICON_PATHS[name]).toBeTruthy();
    }
  });
});
