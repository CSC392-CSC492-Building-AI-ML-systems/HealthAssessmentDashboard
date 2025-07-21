"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import { MagicCard } from "@/components/general/magicui/MagicCard";

type AuthMode = "login" | "signup";

interface AuthFormProps {
    mode: AuthMode;
    onSignup?: (
        email: string,
        password: string,
        organization:
            | { name: string }
            | { name: string; province: string; description: string },
        preferences?: { selected: string[]; custom: string }
    ) => void;
    onLogin?: (
        email: string,
        password: string
    ) => void;
}


const AuthPage: React.FC<AuthFormProps> = ({ mode, onSignup, onLogin }) => {
    const [showPassword, setShowPassword] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    // SIGNUP STEP
    const [step, setStep] = useState(1);

    // CHECK SAME PASSWORD FOR SIGNUP
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // ALL POSSIBLE ERRORS FOR RED SUPPORTING TEXT
    const [errors, setErrors] = useState<{
        email?: string;
        password?: string;
        confirmPassword?: string;
        newOrgName?: string;
        newOrgProvince?: string;
        newOrgDescription?: string;
        existingOrg?: string;
    }>({});

    // PREFERENCES INFO TO ONBOARD
    const [preferences, setPreferences] = useState<string[]>([]);
    const [customPreference, setCustomPreference] = useState("");

    // ORGANIZATION INFO TO ONBOARD
    // Here, we should get the organizations list from the backend API call (DO THIS AS PART OF OUR-47)
    const [organizations, setOrganizations] = useState<string[]>(["test"]);
    const [useExistingOrg, setUseExistingOrg] = useState(true);
    const [selectedOrg, setSelectedOrg] = useState("");
    const [newOrg, setNewOrg] = useState({
        name: "",
        province: "",
        description: "",
    });

    const provinces = [
        "Alberta",
        "British Columbia",
        "Manitoba",
        "New Brunswick",
        "Newfoundland and Labrador",
        "Nova Scotia",
        "Ontario",
        "Prince Edward Island",
        "Quebec",
        "Saskatchewan",
        "Northwest Territories",
        "Nunavut",
        "Yukon",
    ]

    const therapeuticAreas = [
        "Oncology",
        "Cardiology",
        "Neurology",
        "Endocrinology",
        "Dermatology",
        "Respiratory",
        "Urology",
        "Ophthalmology"]

    function resetAuthForm(type: string) {
        if (type === "signup") {
            setEmail("");
            setPassword("");
            setConfirmPassword("");
            setPreferences([]);
            setCustomPreference("");
            setSelectedOrg("");
            setUseExistingOrg(true);
            setNewOrg({ name: "", province: "", description: "" });
        } else if (type === "login") {
            setEmail("");
            setPassword("");
        } else {
            console.log("Invalid auth form type.");
        }

    }

    const handleNextPage = (e: React.FormEvent) => {
        e.preventDefault();
        const newErrors: { email?: string; password?: string; confirmPassword?: string } = {};

        if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = "Please enter a valid email address.";
        }

        if (password.length < 8) {
            newErrors.password = "Password must be at least 8 characters long.";
            newErrors.confirmPassword = "Password must be at least 8 characters long.";
        }

        if (confirmPassword !== password) {
            newErrors.password = "Passwords must match";
            newErrors.confirmPassword = "Passwords must match.";
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length === 0) {
            setStep(step + 1)
        }

    };

    const handleSignup = (e: React.FormEvent) => {
        e.preventDefault();
        const newErrors: { newOrgName?: string; newOrgProvince?: string; newOrgDescription?: string; existingOrg?: string } = {};

        if (!useExistingOrg) {
            if (!newOrg.name) {
                newErrors.newOrgName = "Please enter an organization name."
            }

            if (organizations.includes(newOrg.name)) {
                newErrors.newOrgName = "Already existing organization name."
            }

            if (!newOrg.province) {
                newErrors.newOrgProvince = "Please add a province."
            }

            if (!newOrg.description) {
                newErrors.newOrgDescription = "Please describe the organization."
            }
        } else {
            if (!selectedOrg) {
                newErrors.existingOrg = "Please select a registered organization."
            }
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length === 0) {
            if (!onSignup) {
                throw new Error("No signup function passed to from the client.");
            }

            onSignup(
                email,
                password,
                useExistingOrg
                    ? { name: selectedOrg }
                    : {
                        name: newOrg.name,
                        province: newOrg.province,
                        description: newOrg.description,
                    },
                {
                    selected: preferences,
                    custom: customPreference.trim(),
                }
            );

            resetAuthForm("signup");
        }
    };

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        const newErrors: { email?: string; password?: string; confirmPassword?: string; newOrgName?: string } = {};

        if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = "Please enter a valid email address.";
        }

        if (password.length < 8) {
            newErrors.password = "Password must be at least 8 characters long.";
            newErrors.confirmPassword = "Password must be at least 8 characters long.";
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length === 0) {
            if (onLogin) {
                onLogin(email, password);
            }

            resetAuthForm("login");
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[80vh] bg-[var(--background)]">
            <motion.div
                className="max-w-xl w-full rounded-lg shadow-md bg-var(--brand-light) shadow-xl"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
            >
                <MagicCard gradientColor="var(--gradient-color)">
                    <div className="pt-6 pb-3 text-center font-bold text-2xl">
                        {mode === "login" ? "Welcome to OurPATHS" : "Join OurPATHS"}
                    </div>
                    <div className="pl-6 pr-6">
                        <form onSubmit={mode === "login" ? handleLogin : handleSignup}>
                            {mode === "login" && (
                                <div>
                                    <div className="mb-[20px]">
                                        <label htmlFor="email" className="block text-lg mb-2 font-semibold">
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
                                        {errors.email && <p className="text-red-500 mt-2 text-sm">{errors.email}</p>}
                                    </div>

                                    <div className="mb-6">
                                        <label htmlFor="password" className="block text-lg mb-2 font-semibold">
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
                                        </div>

                                        {errors.password && (
                                            <p className="text-red-500 mt-2 text-sm">{errors.password}</p>
                                        )}
                                    </div>
                                </div>
                            )}

                            {mode === "signup" && (
                                <div>
                                    {step === 1 && (
                                        <div>
                                            <div className="mb-[20px]">
                                                <label htmlFor="email" className="block text-lg mb-2 font-semibold">
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
                                                {errors.email && <p className="text-red-500 mt-2 text-sm">{errors.email}</p>}
                                            </div>

                                            <div className="mb-6">
                                                <label htmlFor="password" className="block text-lg mb-2 font-semibold">
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
                                                </div>

                                                {errors.password && (
                                                    <p className="text-red-500 mt-2 text-sm">{errors.password}</p>
                                                )}
                                            </div>
                                            <div className="mb-6">
                                                <label htmlFor="confirmPassword" className="block text-lg mb-2 font-semibold">
                                                    Confirm Password
                                                </label>
                                                <div className="relative">
                                                    <input
                                                        id="confirmPassword"
                                                        type={showConfirmPassword ? "text" : "password"}
                                                        placeholder="••••••••••"
                                                        value={confirmPassword}
                                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                                        className={`w-full px-4 py-3 pr-12 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.confirmPassword
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
                                                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                                        className="absolute top-1/2 right-4 -translate-y-1/2 text-[var(--brand-light)] hover:text-[var(--button-red)]"
                                                        aria-label="Toggle password visibility"
                                                    >
                                                        {showConfirmPassword ? <EyeOff size={25} /> : <Eye size={25} />}
                                                    </button>
                                                </div>
                                                {errors.confirmPassword && <p className="text-red-500 mt-2 text-sm">{errors.confirmPassword}</p>}

                                            </div>
                                        </div>
                                    )}

                                    {step === 2 && (
                                        <div>
                                            <div className="mb-6">
                                                <label className="block text-lg mb-2 font-semibold">News Preferences</label>
                                                <div className="flex flex-wrap gap-2 mb-4 justify-center">
                                                    {therapeuticAreas.map((pref) => (
                                                        <button
                                                            key={pref}
                                                            type="button"
                                                            className={`px-3 py-1 rounded-full border font-medium transition ${preferences.includes(pref)
                                                                ? "bg-[var(--button-red)] text-white border-transparent"
                                                                : "bg-white text-[var(--brand-dark)] border-gray-300"
                                                                }`}
                                                            onClick={() =>
                                                                setPreferences((prev) =>
                                                                    prev.includes(pref)
                                                                        ? prev.filter((p) => p !== pref)
                                                                        : [...prev, pref]
                                                                )
                                                            }
                                                        >
                                                            {pref}
                                                        </button>
                                                    ))}
                                                </div>

                                                <textarea
                                                    rows={3}
                                                    placeholder="Or describe your news preferences here..."
                                                    value={customPreference}
                                                    onChange={(e) => setCustomPreference(e.target.value)}
                                                    className="w-full px-4 py-2 rounded-lg shadow-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[var(--button-red)]"
                                                    style={{
                                                        backgroundColor: "white",
                                                        color: "var(--brand-dark)",
                                                        fontFamily: "var(--font-body)",
                                                    }}
                                                />
                                            </div>

                                            <div className="mb-6">
                                                <div className="block text-lg font-semibold mb-2">Organization</div>

                                                <div className="mb-4">
                                                    <label className="mr-4">
                                                        <input
                                                            type="radio"
                                                            name="orgOption"
                                                            checked={useExistingOrg}
                                                            onChange={() => setUseExistingOrg(true)}
                                                            className="mr-1 accent-[var(--button-red)]"
                                                        />
                                                        Select existing organization
                                                    </label>
                                                    <label>
                                                        <input
                                                            type="radio"
                                                            name="orgOption"
                                                            checked={!useExistingOrg}
                                                            onChange={() => setUseExistingOrg(false)}
                                                            className="mr-1 accent-[var(--button-red)]"
                                                        />
                                                        Register new organization
                                                    </label>
                                                </div>

                                                {useExistingOrg ? (
                                                    <div>
                                                        <select
                                                            value={selectedOrg}
                                                            onChange={(e) => setSelectedOrg(e.target.value)}
                                                            className={`w-full px-4 py-2 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.existingOrg
                                                                ? "border-2 border-red-500 focus:ring-red-500"
                                                                : "focus:ring-[var(--button-red)]"
                                                                }`}
                                                            style={{
                                                                backgroundColor: "white",
                                                                color: "var(--brand-dark)",
                                                                fontFamily: "var(--font-body)",
                                                            }}
                                                        >
                                                            <option value="">-- Select a registered organization --</option>
                                                            {organizations.map((org) => (
                                                                <option key={org} value={org}>
                                                                    {org}
                                                                </option>
                                                            ))}

                                                        </select>
                                                        {errors.existingOrg && (
                                                            <p className="text-red-500 text-sm mt-1">{errors.existingOrg}</p>
                                                        )}
                                                    </div>
                                                ) : (
                                                    <>
                                                        <div className="mb-3">
                                                            <input
                                                                type="text"
                                                                placeholder="Organization name"
                                                                value={newOrg.name}
                                                                onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
                                                                className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.newOrgName
                                                                    ? "border-2 border-red-500 focus:ring-red-500"
                                                                    : "focus:ring-[var(--button-red)]"
                                                                    }`}
                                                                style={{
                                                                    backgroundColor: "white",
                                                                    color: "var(--brand-dark)",
                                                                    fontFamily: "var(--font-body)",
                                                                }}
                                                            />
                                                            {errors.newOrgName && (
                                                                <p className="text-red-500 text-sm mt-1">{errors.newOrgName}</p>
                                                            )}
                                                        </div>

                                                        <div className="mb-3">
                                                            <select
                                                                value={newOrg.province}
                                                                onChange={(e) => setNewOrg({ ...newOrg, province: e.target.value })}
                                                                className={`w-full px-4 py-2 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.newOrgProvince
                                                                    ? "border-2 border-red-500 focus:ring-red-500"
                                                                    : "focus:ring-[var(--button-red)]"
                                                                    }`}
                                                                style={{
                                                                    backgroundColor: "white",
                                                                    color: "var(--brand-dark)",
                                                                    fontFamily: "var(--font-body)",
                                                                }}
                                                            >
                                                                <option value="">-- Select a province --</option>
                                                                {provinces.map((prov) => (
                                                                    <option key={prov} value={prov}>
                                                                        {prov}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                            {errors.newOrgProvince && (
                                                                <p className="text-red-500 text-sm mt-1">{errors.newOrgProvince}</p>
                                                            )}
                                                        </div>

                                                        <textarea
                                                            rows={3}
                                                            placeholder="Describe the organization..."
                                                            value={newOrg.description}
                                                            onChange={(e) => setNewOrg({ ...newOrg, description: e.target.value })}
                                                            className={`w-full px-4 py-2 rounded-lg shadow-md focus:outline-none focus:ring-2 ${errors.newOrgDescription
                                                                ? "border-2 border-red-500 focus:ring-red-500"
                                                                : "focus:ring-[var(--button-red)]"
                                                                }`}
                                                            style={{
                                                                backgroundColor: "white",
                                                                color: "var(--brand-dark)",
                                                                fontFamily: "var(--font-body)",
                                                            }}
                                                        />

                                                        {errors.newOrgDescription && (
                                                            <p className="text-red-500 text-sm mt-1">{errors.newOrgDescription}</p>
                                                        )}
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex justify-between mt-4">
                                        {step > 1 && (
                                            <button
                                                type="button"
                                                onClick={() => setStep(step - 1)}
                                                className="px-4 py-2 rounded bg-[var(--button-red)] text-white cursor-pointer hover:bg-[var(--button-onhover-red)] font-medium"
                                                style={step === 2 ? { marginRight: '1rem' } : {}}
                                            >
                                                Back
                                            </button>
                                        )}
                                        {step < 2 ? (
                                            <button
                                                type="button"
                                                onClick={(e) => handleNextPage(e)}
                                                className="ml-auto px-4 py-2 bg-[var(--button-red)] text-white rounded cursor-pointer hover:bg-[var(--button-onhover-red)] font-medium"
                                            >
                                                Next
                                            </button>
                                        ) : (
                                            <button
                                                type="submit"
                                                className="w-full bg-[var(--button-onhover-red)] py-2 rounded text-white font-semibold duration-300 cursor-pointer hover:bg-[var(--button-red)] hover:shadow-xl transition"
                                            >
                                                Sign Up
                                            </button>
                                        )}
                                    </div>

                                </div>
                            )}

                            {mode === "login" && (
                                <button
                                    type="submit"
                                    className="w-full bg-[var(--button-onhover-red)] py-2 rounded text-white font-semibold duration-300 cursor-pointer hover:bg-[var(--button-red)] hover:shadow-xl transition"
                                >
                                    {mode === "login" ? "Login" : "Sign Up"}
                                </button>
                            )}
                        </form>
                    </div>

                    <div className="p-4 text-center text-sm">
                        {mode === "login" ? (
                            <>
                                <span className="font-semibold">Not using OurPATHS yet? </span>
                                <a
                                    href="/signup"
                                    className="underline hover:text-[var(--text-onhover-red)] transition"
                                >
                                    Create an account
                                </a>
                            </>
                        ) : (
                            <>
                                <span className="font-semibold">Already have an account? </span>
                                <a
                                    href="/login"
                                    className="underline hover:text-[var(--text-onhover-red)] transition"
                                >
                                    Log in
                                </a>
                            </>
                        )}
                    </div>

                </MagicCard>
            </motion.div>
        </div>
    );
};

export default AuthPage;
