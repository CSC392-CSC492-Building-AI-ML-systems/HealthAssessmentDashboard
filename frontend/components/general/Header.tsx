"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Toggle from "./Toggle";

const Header: React.FC = () => {
    return (
        <nav className="bg-foreground px-4 sm:px-6 md:px-8 lg:px-16 py-4 flex items-center justify-between sticky top-0 z-50">
            {/* OurPaths Logo on Left */}
            <div className="flex items-center space-x-2">
                <img src="/logo.png" alt="logo" className="w-6 h-6" />
                <span className="text-[var(--text-light)]-300 font-semibold text-lg">OurPATHS</span>
            </div>

            {/* Home, About, Contact at Center/Right */}
            <div className="flex space-x-6 text-[var(--text-light)] ml-10 sm:ml-16 md:ml-24 lg:ml-170">
                <a href="#" className="hover:text-gray-400">Home</a>
                <a href="#" className="hover:text-gray-400">About</a>
                <a href="#" className="hover:text-gray-400">Contact</a>
            </div>

            {/* Login & Dark Mode buttons on Right */}
            <div className="flex items-center space-x-4">
                {/* Dark Mode Toggle */}
                <div className="flex items-center space-x-4">
                <Toggle />
                <div className="w-[120px] h-10" /> {/* Placeholder for Login button */}
            </div> 
            </div>
        </nav>
    );
}

export default Header;