"use client";

import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import Link from 'next/link';
import React, { useEffect, useState } from "react";
import Toggle from "../theme/Toggle";
import Login from "../LoginButton";
import Chatbot from "../ChatbotButton";
import SearchBar from "../SearchBar";

type HeaderMode = "full" | "logo-only" | "dashboard";

interface HeaderProps {
    mode?: HeaderMode;
}


const Header: React.FC<HeaderProps> = ({ mode = "full" }) => {
    const { theme } = useTheme();

    const logo =
        theme === "dark"
            ? "/ourpaths-light.png"
            : "/ourpaths-dark.png";

    return (
        <nav className="bg-[var(--background)] px-4 sm:px-6 md:px-8 lg:px-16 py-1 flex items-center justify-between sticky top-0 z-50">

            {/* Logo */}
            <div className="flex items-center space-x-2">
                <img src={logo} alt="OURPATHS logo" className="h-20 w-auto" />
                {/* <span className="text-[var(--text-light)] font-semibold text-lg">OurPATHS</span> */}
            </div>

            {/* Full or Dashboard */}
            {mode === "full" ? (
                <div className="flex items-center space-x-6 text-[var(--text-light)]">
                    <Link href="/" className="hover:text-gray-400">Home</Link>
                    <Link href="/about" className="hover:text-gray-400">About</Link>
                    <Link href="/contact" className="hover:text-gray-400">Contact</Link>
                    <Login />
                    <Toggle />
                </div>
                // Dashboard has Account, Contact, Chatbot and Toggle Buttons
            ) : mode === "dashboard" ? (
                <div className="flex items-center justify-between w-full text-[var(--foreground)]">
               
              
                  {/* SearchBar */}
                  <div className="flex justify-center w-full">
                    <SearchBar />
                  </div>
              
                  {/* Nav Buttons and Account Button */}
                  <div className="flex items-center space-x-6">
                    <Link href="/account" className="hover:text-[var(--foreground)]-400">Account</Link>
                    <Link href="/contact" className="hover:text-[var(--foreground)]-400">Contact</Link>
                    <Chatbot />
                    <Toggle />
                  </div>
                </div>
              ) : null}
              
        </nav>
    
    );
}

export default Header;