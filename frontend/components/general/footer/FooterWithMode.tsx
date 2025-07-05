"use client";

import { usePathname } from 'next/navigation';
import Footer from './Footer';

const FooterWithMode: React.FC = () => {
    // SET THE CORRECT FOOTER BASED ON THE PATHNAME
    const pathname = usePathname();

    const getFooterMode = () => {
        if (pathname === "/landing" || pathname === "/contact" || pathname === "/about") return "full";
        return "empty";
    };

    return (
        <Footer mode={getFooterMode()} />
    )
}

export default FooterWithMode;