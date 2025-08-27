"use client";

import React, { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Sun, Moon } from "lucide-react";

const Toggle = () => {
  const { systemTheme, theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, [])

  if (!mounted) return null;

  const currentTheme = theme === 'system' ?
    systemTheme : theme;

  return (
    <div>
      {currentTheme === 'dark' ? (
        <button className="bg-[var(--brand-light)] text-[var(--brand-dark)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
          onClick={() => setTheme("light")}>
          <Sun></Sun>
        </button>
      ) : (
        <button className="bg-[var(--brand-dark)] text-[var(--brand-light)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:light-xl"
          onClick={() => setTheme("dark")}>
          <Moon></Moon>
        </button>
      )}
    </div>
  );
};

export default Toggle;
