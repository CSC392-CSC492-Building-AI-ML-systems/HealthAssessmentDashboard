"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { Plus } from 'lucide-react';

export const DrugButton = () => {
  const router = useRouter();
  const handleGetStarted = () => {
    router.push("/addDrug");
  };
  return (
    <div className="flex justify-center">
      <button
        onClick={handleGetStarted}
        className="bg-[var(--button-red)] opacity-100 text-[var(--light-color)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:opacity-90 hover:shadow-xl"
      >
        <Plus/>
      </button>
    </div>
  );
};

export default DrugButton;