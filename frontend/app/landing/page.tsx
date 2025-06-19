"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Hero from "@/components/landing/Hero";
import { Marquee } from "@/components/general/magicui/Marquee";
import FAQ from "@/components/landing/FAQ";
import Summary from "@/components/landing/Summary";
import FeatureOverview from "@/components/landing/FeatureOverview";

const Landing: React.FC = () => {
    return (
        <div>
        <Hero/>
        <Summary/>
        <div className="py-4" style={{ backgroundColor: "#0C1821" }}>
        <Marquee reverse pauseOnHover repeat={4}>
            {[
            { src: "/partners/cda.png", alt: "CDA" },
            { src: "/partners/inesss.png", alt: "INESS" },
            { src: "/partners/pcpa.svg", alt: "pCPA"},
            { src: "/partners/sanofi.png", alt: "Sanofi" },
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
        {/* FAQ seems to not have icons... delaying incorporation for now. */}
        <FeatureOverview/>
        <FAQ/>
        </div>
    );
}

export default Landing;