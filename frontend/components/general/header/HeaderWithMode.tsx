"use client";

import { usePathname } from 'next/navigation';
import Header, { HeaderMode } from './Header';

const HeaderWithMode: React.FC = () => {
    // SET THE CORRECT HEADER BASED ON THE PATHNAME
    const pathname = usePathname();

    const getHeaderMode = (): HeaderMode | "none" => {
        if (pathname === "/chatbot") return "none";
        if (pathname === "/landing" || pathname === "/contact" || pathname === "/about") return "full";
        return "logo-only";
    };

    const mode = getHeaderMode();

    if (mode === "none") return null;

    return <Header mode={mode} />;
};

export default HeaderWithMode;