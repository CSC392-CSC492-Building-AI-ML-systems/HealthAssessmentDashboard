"use client";

import React from "react";
import AuthPage from "@/components/auth/AuthPage";
import { useSignupFlow } from "../../hooks/useSignupFlow";
import type { OrganizationType, UserPreferences } from "./types";

const Signup: React.FC = () => {
    const { isLoading, handleSignup } = useSignupFlow();

    const onSignup = async (
        email: string,
        firstName: string,
        lastName: string,
        password: string,
        // organization: OrganizationType,
        preferences?: UserPreferences
    ) => {
        await handleSignup(email, firstName, lastName, password, /* organization, */ preferences);
    };

    return (
        <AuthPage 
            mode="signup" 
            onSignup={onSignup}
            isLoading={isLoading}
        />
    );
};

export default Signup;