"use client";

import { useRouter } from "next/navigation";
import React from "react";
import Image from "next/image";

const FeatureOverview: React.FC = () => {
    const router = useRouter();

    const handleGetStarted = () => {
        router.push("/signup"); // Final path TBD
    };

    return (
        <div className="py-16 px-6 sm:px-12 lg:px-24 bg-background text-foreground">
            {/* Section Heading */}
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-7">
                Integrated Intelligence for Strategic Decision-Making
            </h2>
            <p className="text-center max-w-3xl mx-auto mb-6">
                OurPATHS combines two core capabilities: a data-driven dashboard and an AI-powered conversational assistant to support pharmaceutical stakeholders in optimizing regulatory and reimbursement strategies. This dual-functionality enables both in-depth analysis and accessible interaction with complex data.
            </p>

            {/* Features*/}
            <div className="flex flex-col lg:flex-row justify-center items-stretch gap-8">
                {/* Dashboard */}
                <div className="bg-[var(--feature-bg)] flex-1 p-6 rounded-2xl shadow-lg flex flex-col items-center text-center">
                    <Image
                        src="/dashboardpreview-dark.png"
                        alt="Analytical Dashboard"
                        width={640}
                        height={400}
                        className="w-full h-[400px] object-cover rounded-lg mb-4"
                    />
                    <h3 className="text-xl font-semibold mb-2 text-[var(--brand-dark)]">Analytical Dashboard</h3>
                    <p className="text-sm text-[var(--brand-dark)]">
                        The interactive dashboard aggregates and visualizes historical data from pCPA, CDA, and INESSS. Users can filter by therapeutic area, manufacturer, or indication to identify precedent trends in pricing, negotiation timelines, and reimbursement outcomes. This facilitates evidence-informed planning and strategic benchmarking.g.
                    </p>
                </div>

                {/* Chatbot */}
                <div className="bg-[var(--feature-bg)] flex-1 p-6 rounded-2xl shadow-lg flex flex-col items-center text-center">
                    <Image
                        src="/chatbotpreview-dark.png"
                        alt="Chatbot Assistant"
                        width={640}
                        height={400}
                        className="w-full h-[400px] object-cover rounded-lg mb-4"
                    />
                    <h3 className="text-xl font-semibold mb-2 text-[var(--brand-dark)]">Chatbot Query Assistant</h3>
                    <p className="text-sm text-[var(--brand-dark)]">
                        Our chatbot  assistant allows users to engage directly with structured datasets through intelligent querying. OurPATHS users can explore approval patterns, pricing precedents, and potential timelines by asking domain-relevant questions, and reduce the time spent navigating complex datasets while maintaining analytical depth.
                    </p>
                </div>
            </div>

            {/* Get Started Button - can replace with Create Account Button */}
            <div className="flex justify-center mt-8">
                <button
                    onClick={handleGetStarted}
                    className="bg-[var(--button-red)] text-[var(--text-light)] font-semibold px-6 py-3 rounded-full transition-transform duration-300 hover:scale-105 hover:shadow-xl"
                >
                    Get Started
                </button>
            </div>
        </div>
    );
};

export default FeatureOverview;
