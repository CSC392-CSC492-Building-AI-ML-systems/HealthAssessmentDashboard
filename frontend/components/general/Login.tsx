"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

const Login = () => {
  const router = useRouter();

    const handleGetStarted = () => {
        router.push("/signup");
    };
  return (
    <div className="flex justify-center">
                <button
                onClick={handleGetStarted}
                    className="bg-[var(--button-red)] text-[var(--text-light)] font-semibold px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
                >
                    Login / Sign up
                </button>
            </div>
  );
};

export default Login;