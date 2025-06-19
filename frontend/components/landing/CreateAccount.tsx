"use client";

import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import React from "react";

const CreateAccountButton: React.FC = () => {
  const router = useRouter();

  const handleClick = () => {
    router.push("/signup");
  };

  return (
    <button
      onClick={handleClick}
      className="group flex items-center gap-3 px-6 py-3 rounded-full border-4 border-[#0c1a24] dark:border-[#c7c5dd] bg-transparent text-[#0c1a24] dark:text-[#c7c5dd] text-lg font-semibold transition-all hover:bg-[#0c1a24]/10 dark:hover:bg-white/10"
    >
      Create an account
      <ArrowRight
        className="transition-transform group-hover:translate-x-1"
        size={20}
      />
    </button>
  );
};

export default CreateAccountButton;
