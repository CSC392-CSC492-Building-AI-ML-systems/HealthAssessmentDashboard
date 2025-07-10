"use client";

import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import Link from 'next/link';
import React, { useEffect, useState } from "react";
import Toggle from "./theme/Toggle";
import Login from "./Login";

const Header: React.FC = () => {
    const { theme } = useTheme();

    const logo =
    theme === "dark"
      ? "/ourpaths-light.png"
      : "/ourpaths-dark.png";

    return (
        <nav className="bg-[var(--headerfooter)] px-4 sm:px-6 md:px-8 lg:px-16 py-1 flex items-center justify-between sticky top-0 z-50">

            {/* Logo */}
            <div className="flex items-center space-x-2">
                <img src={logo} alt="OURPATHS logo" className="h-20 w-auto" />
                {/* <span className="text-[var(--text-light)] font-semibold text-lg">OurPATHS</span> */}
            </div>

            {/* Nav Links */}
            <div className="flex items-center space-x-6 text-[var(--text-light)]">
                <Link href="/" className="hover:text-gray-400">Home</Link>
                <Link href="/about" className="hover:text-gray-400">About</Link>
                <Link href="/contact" className="hover:text-gray-400">Contact</Link>
                <Login />
                <Toggle />
            </div>
        </nav>

    );
}

export default Header;