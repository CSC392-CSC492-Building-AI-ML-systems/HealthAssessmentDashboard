"use client";

import { usePathname } from 'next/navigation';
import Header from './Header';

const HeaderWithMode: React.FC = () => {
    // SET THE CORRECT HEADER BASED ON THE PATHNAME
    const pathname = usePathname();

    const getHeaderMode = () => {
        if (pathname === "/landing" || pathname === "/contact" || pathname === "/about")
             return "full";
        else if (pathname.startsWith("/dashboard")) 
            return "dashboard"
        return "logo-only";
    };

    return (
        <Header mode={getHeaderMode()} />
    )
}

export default HeaderWithMode;