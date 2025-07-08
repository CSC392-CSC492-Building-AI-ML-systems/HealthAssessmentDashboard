"use client";

import { useTheme } from "next-themes";

export default function Topbar() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="flex items-center justify-between px-6 py-4 bg-[var(--background)] text-[var(--foreground)] border-b border-[var(--feature-bg)]">
      {/* Left: Logo and title */}
      <div className="flex items-center space-x-2">
        <img src="/ourpaths-light.png" alt="OurPATHS logo" className="h-8 w-auto" />
        <span className="text-lg font-semibold">OurPATHS</span>
      </div>

      {/* Right: Launch + Theme Toggle */}
      <div className="flex items-center space-x-4">
        <a
          href="/dashboard"
          className="bg-[var(--button-red)] text-white px-4 py-2 rounded-full text-sm hover:opacity-90"
        >
          Launch Dashboard
        </a>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="rounded-full w-10 h-5 flex items-center bg-gray-400 dark:bg-gray-700 px-1"
        >
          <div
            className={`w-4 h-4 bg-white rounded-full transition-transform ${
              theme === "dark" ? "translate-x-5" : ""
            }`}
          />
        </button>
      </div>
    </header>
  );
}
