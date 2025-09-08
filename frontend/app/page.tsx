"use client";

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const Home: React.FC = () => {
    const router = useRouter();

    useEffect(() => {
        const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
        router.replace(token ? "/dashboard" : "/landing");
      }, [router]);

    return <div />;
}

export default Home;
