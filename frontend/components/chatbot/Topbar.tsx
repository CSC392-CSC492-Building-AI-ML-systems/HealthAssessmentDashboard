"use client";

import { useTheme } from "next-themes";
import Toggle from "../general/theme/Toggle";


interface TopbarProps {
    onToggleSidebar: () => void;
    }

export default function Topbar({ onToggleSidebar }: TopbarProps) {
    const { theme, setTheme } = useTheme();
    
    const logo =
        theme === "light"
            ? "/ourpaths-dark.png"
            : "/ourpaths-light.png";

    return (
        <header className="flex items-center justify-between px-6 py-4 bg-[var(--bars)] text-[var(--foreground)] border-b-2 border-[var(--feature-bg)]">
        {/* Toggle button + Logo */}
        <div className="flex items-center space-x-4">
            {/* Sidebar toggle */}
            <button
            onClick={onToggleSidebar}
            className="md:hidden text-2xl focus:outline-none"
            title="Toggle Sidebar"
            >
            ☰
            </button>

            {/*:Logos switch according to theme*/}
            <img src={logo} alt="OurPATHS logo" className="h-12 w-auto" />
        </div>

        {/* Right: Launch Dashboard + Theme Toggle */}
        <div className="flex items-center space-x-4">
            <a
            href="/dashboard"
            className="bg-[var(--button-red)] text-white px-4 py-2 rounded-full text-sm hover:opacity-90"
            >
            Dashboard
            </a>

            {/* Theme Toggle */}        
            <Toggle />
            
            {/* <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="rounded-full w-10 h-5 flex items-center bg-gray-400 dark:bg-gray-700 px-1"
            >
            <div
                className={`w-4 h-4 bg-white rounded-full transition-transform ${
                theme === "light" ? "" : "translate-x-5"
                }`}
            />
            </button> */}

        </div>
        </header>
    );
    }
