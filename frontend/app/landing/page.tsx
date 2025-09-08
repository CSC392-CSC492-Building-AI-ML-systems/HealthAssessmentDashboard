"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Hero from "@/components/landing/Hero";
import { Marquee } from "@/components/general/magicui/Marquee";
import FAQ from "@/components/landing/FAQ";
import Summary from "@/components/landing/Summary";
import FeatureOverview from "@/components/landing/FeatureOverview";

const Landing: React.FC = () => {
    const router = useRouter();

    useEffect(() => {
        const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
        if (token) router.replace("/dashboard");
      }, [router]);
      
    return (
        <div>
        <Hero/>
        <Summary/>
        <div className="py-4" style={{ backgroundColor: "#0C1821" }}>
        <Marquee reverse pauseOnHover repeat={4}>
            {[
            { src: "/sources/cda.png", alt: "CDA" },
            { src: "/sources/inesss.png", alt: "INESS" },
            { src: "/sources/pcpa.svg", alt: "pCPA"},
            ].map((logo, index) => (
            <div
                key={index}
                className="h-12 w-40 flex items-center justify-center mx-3 shrink-0"
            >
                <img
                src={logo.src}
                alt={logo.alt}
                className="max-h-full max-w-full object-contain"
                />
            </div>
            ))}
        </Marquee>
        </div>
        <FeatureOverview/>
        <FAQ/>
        </div>
    );
}

export default Landing;