"use client";

import React from "react";
import AuthPage from "@/components/auth/AuthPage"

const Login: React.FC = () => {
    const onLogin = (email: string, password: string) => {
        console.log("LOGIC HERE");
    }

    return (
        <AuthPage mode={"login"} onLogin={onLogin} />
    );
}

export default Login;