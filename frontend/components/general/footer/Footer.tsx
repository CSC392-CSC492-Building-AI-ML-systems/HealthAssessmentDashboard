"use client";

import React from "react";
import Link from 'next/link';

type FooterMode = "full" | "empty";

interface FooterProps {
  mode?: FooterMode;
}

const Footer: React.FC<FooterProps> = ({ mode = "full" }) => {
  if (mode === "empty") {
    return <div className="h-[64px] px-6 py-4" />;
  }

  return (
    <footer className="bg-[var(--background)] text-[var(--text-light)] px-6 py-4 flex justify-between items-center">
      {/* Copyright on left */}
      <div className="flex space-x-3 px-5 text-sm">
        © Copyright OurPATHS 2025
      </div>
      {/* Logo to be Added*/}
      {/* Home, About & Contact on right */}
      <div className="flex space-x-10 px-10 text-sm">
        <Link href="/" className="hover:text-gray-400">Home</Link>
        <Link href="/about" className="hover:text-gray-400">About</Link>
        <Link href="/contact" className="hover:text-gray-400">Contact</Link>
      </div>
    </footer>
  );
};

export default Footer;


