"use client";

import React from "react";
import AuthPage from "@/components/auth/AuthPage"

const Signup: React.FC = () => {
    const handleSignup = (
        email: string,
        password: string,
        organization:
            | { name: string }
            | { name: string; province: string; description: string },
        preferences?: { selected: string[]; custom: string }
    ) => {
        console.log("LOGIC HERE");
    };

    return (
        <AuthPage mode={"signup"} onSignup={handleSignup} />
    );
}

export default Signup;