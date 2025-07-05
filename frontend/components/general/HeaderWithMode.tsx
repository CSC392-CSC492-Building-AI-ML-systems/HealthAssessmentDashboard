"use client";

import { usePathname } from 'next/navigation';
import Header from './Header';

const HeaderWithMode: React.FC = () => {
    // SET THE CORRECT HEADER BASED ON THE PATHNAME
    const pathname = usePathname();

    const getHeaderMode = () => {
        if (pathname === "/landing") return "full";
        return "logo-only";
    };

    return (
        <Header mode={getHeaderMode()} />
    )
}

export default HeaderWithMode;