import { useEffect, useState } from "react";

export type Theme = "light" | "dark" | "system";

export const THEMES: Theme[] = ["light", "dark", "system"];

export function resolveDark(theme: Theme, systemPrefersDark: boolean): boolean {
  if (theme === "system") return systemPrefersDark;

  return theme === "dark";
}

function systemPrefersDark(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem("theme");

    return THEMES.includes(stored as Theme) ? (stored as Theme) : "system";
  });
  const [dark, setDark] = useState(() => resolveDark(theme, systemPrefersDark()));

  useEffect(() => {
    localStorage.setItem("theme", theme);

    const apply = () => {
      const isDark = resolveDark(theme, systemPrefersDark());
      setDark(isDark);
      document.documentElement.classList.toggle("dark", isDark);
    };

    apply();

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    media.addEventListener("change", apply);

    return () => media.removeEventListener("change", apply);
  }, [theme]);

  return { theme, setTheme, dark };
}
