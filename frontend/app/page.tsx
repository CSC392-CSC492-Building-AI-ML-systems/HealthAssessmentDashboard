"use client";

import { useRouter } from "next/navigation";
import { useEffect } from 'react';

const Home: React.FC = () => {
    const router = useRouter();

    useEffect(() => {
        router.push('/landing');
    }, [router]);

    return <div />;
}

export default Home;
