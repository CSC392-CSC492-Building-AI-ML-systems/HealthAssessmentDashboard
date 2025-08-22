"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import AuthPage from "@/components/auth/AuthPage";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/components/general/ToastProvider";

const Login: React.FC = () => {
    const router = useRouter();
    const { showError: showToastError, showInfo } = useToast();
    const { login } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    const onLogin = async (email: string, password: string) => {
        setIsLoading(true);

        try {
            const success = await login(email, password);

            if (success) {
                showInfo("Login successful! Redirecting...", "Welcome Back!");
                
                setTimeout(() => {
                    router.push("/dashboard");
                }, 1500);
            } else {
                showToastError("Invalid email or password. Please try again.", "Login Failed");
            }
        } catch (error) {
            let errorMessage = "An unexpected error occurred during login";
            let errorTitle = "Login Failed";
            
            if (error instanceof Error) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error && typeof error === 'object') {
                const apiError = error as any;
                errorMessage = apiError.detail || apiError.message || errorMessage;
                errorTitle = apiError.title || errorTitle;
            }
            showToastError(errorMessage, errorTitle);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <AuthPage 
            mode="login" 
            onLogin={onLogin}
            isLoading={isLoading}
        />
    );
}

export default Login;