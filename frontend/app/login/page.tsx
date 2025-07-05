"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import React, { useEffect, useState } from "react";
import { MagicCard } from "@/components/general/magicui/MagicCard"
import { Eye, EyeOff } from "lucide-react";
import AuthPage from "@/components/auth/AuthPage"

const Login: React.FC = () => {
    return (
        <AuthPage />
    );
}

export default Login;