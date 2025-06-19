"use client";

import { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";

const Toggle = () => {
  return (
    <button
      className="flex items-center space-x-2 px-3 py-2 rounded-full bg-gray-300 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 transition"
    >
      <Sun className="w-6 h-6 text-[var(--text-light)]-500" />
      {/* <Moon className="w-5 h-5 text-gray-800 dark:text-[var(--text-light)]" /> */}
    </button>
  );
};

export default Toggle;
