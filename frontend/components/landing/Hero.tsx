"use client";

import Image from "next/image";
import React from "react";
import CreateAccountButton from "./CreateAccount";

const Hero: React.FC = () => {
  return (
    <section className="w-full bg-[#0C1821] text-white py-16 px-4 relative overflow-hidden">
      {/* Background Globe */}
      <img
        src="/globe.svg"
        alt="Globe Background"
        className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[80vw] max-w-[600px] opacity-10 z-0 pointer-events-none"
      />
      <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
        
        {/* Left: Logo only */}
        <div className="flex items-center">
          <Image
            src="/ourpathsexp-light.png" 
            alt="OurPATHS Logo"
            width={600}
            height={40}
            priority
          />
        </div>

        {/* Right: Create Account Button */}
        <div className="flex justify-end pr-6 sm:pr-10 md:pr-14">
            <CreateAccountButton />
        </div>
      </div>
    </section>
  );
};

export default Hero;
