"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Code, Clock, Globe } from "lucide-react";

const Contact: React.FC = () => {
    return (
        
        <div className="font-[var(--font-body)] bg-[var(--background)] text-[var(--text-light)] font-sans px-6 py-4">
            {/* Brand label*/}
            <div className = "relative overflow-hidden">
            <img src="/globe.svg" alt="Globe" className="mx-auto absolute left-1/2 top-1/2 -translate-y-1/2 w-[80vw] max-w-[600px] opacity-10 z-0" />
            <img src="/ourpathsexp-light.png" alt="OurPATHS Logo" className="w-160 h-auto z-50" />
            </div>

            {/* Emails and other contact information.
            /* Ensure contact points are adjusted horizontally and evenly.
            /* Only one email shown per scroll when on mobile. */}
            <section className = "bg-[var(--text-light)] text-[var(--background)] justify-between text-center grid grid-cols-1 md:grid-cols-3 mx-auto py-32 px-8">
                    {/* For database inquiries */}
                    <div>
                    <p className = "font-bold text-xl"> For database inquiries:</p>
                    <a href="#" className="hover:text-gray-400 underline">usage@ourpaths.ca</a>
                    </div>

                    {/* For general inquiries */}
                    <div>
                    <p className = "font-bold text-xl"> For general inquiries:</p>
                    <a href="#" className="hover:text-gray-400 underline">general@ourpaths.ca</a>
                    </div>

                    <div>
                    {/* To report any issues */}
                    <p className = "font-bold text-xl"> To report any issues:</p>
                    <a href="#" className="hover:text-gray-400 underline">contact@ourpaths.ca</a>
                    </div>
            </section>

            {/* Characteristics strip */}
            <div className = "flex text-left justify-center gap-x-100 px-8 py-8 mt-20 text-[var(--text-light)] bg-[var(--background)]">
                <div className = "flex itmes-center space-x-2"> 
                    <Globe className="w-6 h-6 text-[var(--text-light)]-500" />
                    <span>Accessible</span>
                </div>
                <div className = "flex itmes-center space-x-2">
                    <Clock className="w-6 h-6 text-[var(--text-light)]-500" />
                    <span>Quick</span>
                </div>
                <div className = "flex itmes-center space-x-2">
                    <Code className="w-6 h-6 text-[var(--text-light)]-500" />
                    <span>Open-Source</span>
                </div>
            </div>
        </div>
    );
}

export default Contact;
