"use client";

import Image from "next/image";
import React from "react";
import CreateAccountButton from "./CreateAccount";
// import { LogoCarousel } from "./LogoCarousel";

const Hero: React.FC = () => {
  return (
    <section className="w-full bg-[#0c1a24] text-white py-16 px-4">
      <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row justify-between items-center gap-10">
        
        {/* Left: Logo only */}
        <div className="flex items-center">
          <Image
            src="/ourpathsexplogo_dark.png" 
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
