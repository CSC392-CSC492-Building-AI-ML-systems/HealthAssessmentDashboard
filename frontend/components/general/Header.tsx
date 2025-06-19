"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Toggle from "./Toggle";
import Login from "./Login";

const Header: React.FC = () => {
    return (
        <nav className="bg-[var(--background)] px-4 sm:px-6 md:px-8 lg:px-16 py-1 flex items-center justify-between sticky top-0 z-50">

            {/* Logo */}
            <div className="flex items-center space-x-2">
                <img src="/ourpaths-light.png" alt="OURPATHS logo" className="h-20 w-auto" />
                {/* <span className="text-[var(--text-light)] font-semibold text-lg">OurPATHS</span> */}
            </div>

            {/* Nav Links */}
            <div className="flex items-center space-x-6 text-[var(--text-light)]">
                <a href="#" className="hover:text-gray-400">Home</a>
                <a href="#" className="hover:text-gray-400">About</a>
                <a href="#" className="hover:text-gray-400">Contact</a>
                <Login />
                <Toggle />
            </div>
        </nav>

    );
}

export default Header;