"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import React, { useEffect, useState } from "react";
import { MagicCard } from "@/components/general/magicui/MagicCard"
import { Eye, EyeOff } from "lucide-react";

const Login: React.FC = () => {
    const [showPassword, setShowPassword] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const newErrors: { email?: string; password?: string } = {};

        if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = "Please enter a valid email address.";
        }

        if (password.length < 8) {
            newErrors.password = "Password must be at least 8 characters long.";
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length === 0) {
            // ADD LOGIN LOGIC IN NEXT TICKET

            setEmail("")
            setPassword("")
        }
    };


    return (
        <div className="flex items-center justify-center h-[80vh] bg-[var(--background)]">
            <motion.div
                className="max-w-xl w-full rounded-lg shadow-md bg-var(--brand-light) shadow-xl"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}>
                <MagicCard gradientColor="var(--gradient-color)"
                >
                    <div
                        className="pt-6 pb-3 text-center font-bold text-2xl"
                    >
                        Welcome to OurPATHS
                    </div>
                    <div className="pl-6 pr-6">
                        <form onSubmit={handleSubmit}>
                            <div className="mb-[20px]">
                                <label
                                    htmlFor="email"
                                    className="block text-lg mb-2 font-semibold"
                                >
                                    Email
                                </label>
                                <input
                                    id="email"

                                    placeholder="name@email.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.email
                                        ? "border-2 border-red-500 focus:ring-red-500"
                                        : "focus:ring-[var(--button-red)]"
                                        }`}
                                    style={{
                                        backgroundColor: "white",
                                        color: "var(--brand-dark)",
                                        fontFamily: "var(--font-body)",
                                    }}
                                />
                                {errors.email && (
                                    <p className="text-red-500 mt-2 text-sm">{errors.email}</p>
                                )}
                            </div>
                            <div className="mb-6">
                                <label
                                    htmlFor="password"
                                    className="block text-lg mb-2 font-semibold"
                                >
                                    Password
                                </label>

                                <div className="relative">
                                    <input
                                        id="password"
                                        type={showPassword ? "text" : "password"}
                                        placeholder="••••••••••"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className={`w-full px-4 py-3 pr-12 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.password
                                            ? "border-2 border-red-500 focus:ring-red-500"
                                            : "focus:ring-[var(--button-red)]"
                                            }`}
                                        style={{
                                            backgroundColor: "white",
                                            color: "var(--brand-dark)",
                                            fontFamily: "var(--font-body)",
                                        }}
                                    />

                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute top-1/2 right-4 -translate-y-1/2 text-[var(--brand-light)] hover:text-[var(--button-red)]"
                                        aria-label="Toggle password visibility"
                                    >
                                        {showPassword ? <EyeOff size={25} /> : <Eye size={25} />}
                                    </button>
                                    {errors.password && (
                                        <p className="text-red-500 mt-2 text-sm">{errors.password}</p>
                                    )}
                                </div>
                            </div>
                            <button
                                type="submit"
                                className="w-full bg-[var(--button-onhover-red)] py-2 rounded text-white font-semibold duration-300 cursor-pointer hover:bg-[var(--button-red)] hover:shadow-xl transition"
                            >
                                Login
                            </button>
                        </form>
                    </div>

                    <div className="p-4 text-center text-sm">
                        <span className="font-semibold">
                            Not using OurPATHS yet?{" "}
                        </span>
                        <span>
                            <a href="/signup" className="underline hover:text-[var(--text-onhover-red)] transition">
                                Create an account
                            </a>
                        </span>
                    </div>
                </MagicCard>
            </motion.div >
        </div >
    );
}

export default Login;