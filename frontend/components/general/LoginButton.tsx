"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

const LoginButton = () => {
  const router = useRouter();
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  const handleGetStarted = () => {
    router.push("/signup");
  };

  const handleLogin = () => {
    router.push("/login");
  };

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  const handleDashboard = () => {
    router.push("/dashboard");
  };

  if (isLoading) {
    return (
      <div className="animate-pulse bg-gray-300 rounded-full px-3.5 py-2 w-24 h-10"></div>
    );
  }

  if (isAuthenticated && user) {
    return (
      <div className="flex items-center space-x-3">
        <span className="text-[var(--text-light)] text-sm">
          Welcome, {user.first_name}
        </span>
        <button
          onClick={handleDashboard}
          className="bg-[var(--button-red)] text-[var(--feature-bg)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
        >
          Dashboard
        </button>
        <button
          onClick={handleLogout}
          className="border border-[var(--button-red)] text-[var(--button-red)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <button
        onClick={handleLogin}
        className="border border-[var(--button-red)] text-[var(--button-red)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
      >
        Login
      </button>
      <button
        onClick={handleGetStarted}
        className="bg-[var(--button-red)] text-[var(--feature-bg)] px-3.5 py-2 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
      >
        Create an Account
      </button>
    </div>
  );
};

export default LoginButton;