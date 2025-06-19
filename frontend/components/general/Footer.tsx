"use client";

import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="bg-[var(--background)] text-[var(--text-light)] px-6 py-4 flex justify-between items-center">
      {/* Copyright on Left */}
      <div className="flex space-x-3 px-5 ext-sm">
        © Copyright OurPATHS 2025
      </div>

      {/* Home, About & Conact on Right */}
      <div className="flex space-x-10 px-10 text-sm">
        <a href="#" className="hover:text-gray-400">Home</a>
        <a href="#" className="hover:text-gray-400">About</a>
        <a href="#" className="hover:text-gray-400">Contact</a>
      </div>
    </footer>
  );
};

export default Footer;


      