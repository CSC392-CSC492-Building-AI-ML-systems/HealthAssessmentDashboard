"use client";

import React from "react";
import Link from 'next/link';

const Footer: React.FC = () => {
  return (
    <footer className="bg-[var(--background)] text-[var(--text-light)] px-6 py-4 flex justify-between items-center">
      {/* Copyright on left */}
      <div className="flex space-x-3 px-5 ext-sm">
        © Copyright OurPATHS 2025
      </div>
        {/* Logo to be Added*/}
      {/* Home, About & Conact on right */}
      <div className="flex space-x-10 px-10 py-10 text-sm">
        <Link href="/" className="hover:text-gray-400">Home</Link>
        <Link href="/about" className="hover:text-gray-400">About</Link>
        <Link href="/contact" className="hover:text-gray-400">Contact</Link>
      </div>
    </footer>
  );
};

export default Footer;


      