"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import { MagicCard } from "@/components/general/magicui/MagicCard";
import LoadingSpinner from "@/components/general/LoadingSpinner";
import { validateEmail, validateName, validatePassword } from "@/app/signup/utils/validation";

type AuthMode = "login" | "signup";

interface AuthFormProps {
  mode: AuthMode;
  onSignup: (
    email: string,
    firstName: string,
    lastName: string,
    password: string,
    preferences?: { selected: string[]; custom: string }
  ) => void;
  onLogin?: (email: string, password: string) => void;
  isLoading?: boolean;
}

const AuthPage: React.FC<AuthFormProps> = ({ mode, onSignup, onLogin, isLoading = false }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // user info
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  // signup state
  const [step, setStep] = useState(1);

  // preferences
  const [preferences, setPreferences] = useState<string[]>([]);
  const [customPreference, setCustomPreference] = useState("");

  // errors
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
    firstName?: string;
    lastName?: string;
  }>({});

  const therapeuticAreas = [
    "Oncology",
    "Cardiology",
    "Neurology",
    "Endocrinology",
    "Dermatology",
    "Respiratory",
    "Urology",
    "Ophthalmology",
  ];

  function resetAuthForm(type: "signup" | "login") {
    if (type === "signup") {
      setEmail("");
      setPassword("");
      setConfirmPassword("");
      setFirstName("");
      setLastName("");
      setPreferences([]);
      setCustomPreference("");
      setStep(1);
    } else {
      setEmail("");
      setPassword("");
    }
  }

  const handleNextPage = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: typeof errors = {};

    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) newErrors.email = emailValidation.errors[0];

    const firstNameValidation = validateName(firstName, "First name");
    if (!firstNameValidation.isValid) newErrors.firstName = firstNameValidation.errors[0];

    const lastNameValidation = validateName(lastName, "Last name");
    if (!lastNameValidation.isValid) newErrors.lastName = lastNameValidation.errors[0];

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) newErrors.password = passwordValidation.errors[0];

    if (confirmPassword !== password) {
      newErrors.confirmPassword = "Passwords must match.";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      setStep(2);
    }
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();

    onSignup(
      email.trim(),
      firstName.trim(),
      lastName.trim(),
      password,
      {
        selected: preferences,
        custom: customPreference.trim(),
      }
    );

    resetAuthForm("signup");
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: typeof errors = {};

    const emailValidation = validateEmail(email);
    if (!emailValidation.isValid) newErrors.email = emailValidation.errors[0];

    if (!password || password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long.";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0 && onLogin) {
      onLogin(email, password);
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
              {/* LOGIN */}
              {mode === "login" && (
                <div>
                  {/* email */}
                  <div className="mb-[20px]">
                    <label htmlFor="email" className="block text-lg mb-2 font-semibold">
                      Email
                    </label>
                    <input
                      id="email"
                      placeholder="name@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                        errors.email ? "border-2 border-red-500 focus:ring-red-500" : "focus:ring-[var(--button-red)]"
                      }`}
                      style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                    />
                    {errors.email && <p className="text-red-500 mt-2 text-sm">{errors.email}</p>}
                  </div>

                  {/* password */}
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
                        className={`w-full px-4 py-3 pr-12 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                          errors.password ? "border-2 border-red-500 focus:ring-red-500" : "focus:ring-[var(--button-red)]"
                        }`}
                        style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
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
                    {errors.password && <p className="text-red-500 mt-2 text-sm">{errors.password}</p>}
                  </div>
                </div>
              )}

              {/* SIGNUP */}
              {mode === "signup" && (
                <div>
                  {step === 1 && (
                    <div>
                      {/* email */}
                      <div className="mb-[20px]">
                        <label htmlFor="email" className="block text-lg mb-2 font-semibold">
                          Email
                        </label>
                        <input
                          id="email"
                          placeholder="name@email.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                            errors.email ? "border-2 border-red-500 focus:ring-red-500" : "focus:ring-[var(--button-red)]"
                          }`}
                          style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                        />
                        {errors.email && <p className="text-red-500 mt-2 text-sm">{errors.email}</p>}
                      </div>

                      {/* first name */}
                      <div className="mb-[20px]">
                        <label htmlFor="firstName" className="block text-lg mb-2 font-semibold">
                          First Name
                        </label>
                        <input
                          id="firstName"
                          placeholder="John"
                          value={firstName}
                          onChange={(e) => setFirstName(e.target.value)}
                          className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                            errors.firstName ? "border-2 border-red-500 focus:ring-red-500" : "focus:ring-[var(--button-red)]"
                          }`}
                          style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                        />
                        {errors.firstName && <p className="text-red-500 mt-2 text-sm">{errors.firstName}</p>}
                      </div>

                      {/* last name */}
                      <div className="mb-[20px]">
                        <label htmlFor="lastName" className="block text-lg mb-2 font-semibold">
                          Last Name
                        </label>
                        <input
                          id="lastName"
                          placeholder="Doe"
                          value={lastName}
                          onChange={(e) => setLastName(e.target.value)}
                          className={`w-full px-4 py-3 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                            errors.lastName ? "border-2 border-red-500 focus:ring-red-500" : "focus:ring-[var(--button-red)]"
                          }`}
                          style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                        />
                        {errors.lastName && <p className="text-red-500 mt-2 text-sm">{errors.lastName}</p>}
                      </div>

                      {/* password + confirm */}
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
                            className={`w-full px-4 py-3 pr-12 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                              errors.password
                                ? "border-2 border-red-500 focus:ring-red-500"
                                : "focus:ring-[var(--button-red)]"
                            }`}
                            style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
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
                        {errors.password && <p className="text-red-500 mt-2 text-sm">{errors.password}</p>}
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
                            className={`w-full px-4 py-3 pr-12 rounded-lg shadow-md focus:outline-none focus:ring-2 ${
                              errors.confirmPassword
                                ? "border-2 border-red-500 focus:ring-red-500"
                                : "focus:ring-[var(--button-red)]"
                            }`}
                            style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                          />
                          <button
                            type="button"
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            className="absolute top-1/2 right-4 -translate-y-1/2 text-[var(--brand-light)] hover:text-[var(--button-red)]"
                            aria-label="Toggle confirm password visibility"
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
                              className={`px-3 py-1 rounded-full border font-medium transition ${
                                preferences.includes(pref)
                                  ? "bg-[var(--button-red)] text-white border-transparent"
                                  : "bg-white text-[var(--brand-dark)] border-gray-300"
                              }`}
                              onClick={() =>
                                setPreferences((prev) =>
                                  prev.includes(pref) ? prev.filter((p) => p !== pref) : [...prev, pref]
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
                          style={{ backgroundColor: "white", color: "var(--brand-dark)", fontFamily: "var(--font-body)" }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between mt-4">
                    {step > 1 && (
                      <button
                        type="button"
                        onClick={() => setStep(step - 1)}
                        className="px-4 py-2 rounded bg-[var(--button-red)] text-white cursor-pointer hover:bg-[var(--button-onhover-red)] font-medium"
                      >
                        Back
                      </button>
                    )}
                    {step < 2 ? (
                      <button
                        type="button"
                        onClick={handleNextPage}
                        className="ml-auto px-4 py-2 bg-[var(--button-red)] text-white rounded cursor-pointer hover:bg-[var(--button-onhover-red)] font-medium"
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        type="submit"
                        disabled={isLoading}
                        className={`w-full py-2 rounded text-white font-semibold duration-300 transition ${
                          isLoading
                            ? "bg-gray-400 cursor-not-allowed"
                            : "bg-[var(--button-onhover-red)] hover:bg-[var(--button-red)] hover:shadow-xl cursor-pointer"
                        }`}
                      >
                        {isLoading ? (
                          <span className="flex items-center justify-center gap-2">
                            <LoadingSpinner size="sm" />
                            Creating Account...
                          </span>
                        ) : (
                          "Sign Up"
                        )}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* LOGIN button */}
              {mode === "login" && (
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full py-2 rounded text-white font-semibold duration-300 transition ${
                    isLoading
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-[var(--button-onhover-red)] hover:bg-[var(--button-red)] hover:shadow-xl cursor-pointer"
                  }`}
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <LoadingSpinner size="sm" />
                      Logging in...
                    </span>
                  ) : (
                    "Login"
                  )}
                </button>
              )}
            </form>
          </div>

          <div className="p-4 text-center text-sm">
            {mode === "login" ? (
              <>
                <span className="font-semibold">Not using OurPATHS yet? </span>
                <a href="/signup" className="underline hover:text-[var(--text-onhover-red)] transition">
                  Create an account
                </a>
              </>
            ) : (
              <>
                <span className="font-semibold">Already have an account? </span>
                <a href="/login" className="underline hover:text-[var(--text-onhover-red)] transition">
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
