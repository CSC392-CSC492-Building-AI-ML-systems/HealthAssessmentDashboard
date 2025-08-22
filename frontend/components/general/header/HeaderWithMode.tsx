"use client";

import { usePathname } from 'next/navigation';
import Header, { HeaderMode } from './Header';

const HeaderWithMode: React.FC = () => {
    const pathname = usePathname();

    const getHeaderMode = () => {
        if (pathname === "/landing" || pathname === "/contact" || pathname === "/about")
             return "full";
        else if (pathname.startsWith("/dashboard")) 
            return "dashboard"
        else if (pathname === "/chatbot") return "chatbot";
        return "logo-only";
    };

    const mode = getHeaderMode();

    return <Header mode={mode} />;
};

export default HeaderWithMode;