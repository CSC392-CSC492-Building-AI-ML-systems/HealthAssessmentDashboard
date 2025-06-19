"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

const About: React.FC = () => {
    return (
    <div>    
            {/* Brand label*/}
            <div className = "relative overflow-hidden">
            <img src="/globe.svg" alt="Globe" className="mx-auto absolute left-1/2 top-1/2 -translate-y-1/2 w-[80vw] max-w-[600px] opacity-10 z-0" />
            <img src="/ourpathsexp-light.png" alt="OurPATHS Logo" className="w-160 h-auto z-50" />
            </div>

      {/* Overview paragraph */}
      <div className="bg-[var(--brand-light)] text-[var(--brand-dark)] py-10 px-4 sm:px-8 lg:px-32">
        <p>
          OurPATHS is a decision-support platform designed to assist pharmaceutical stakeholders
          in navigating Canada’s complex market access landscape.
        </p>
        <p className="mt-4">
          By integrating structured data from agencies such as pCPA, CDA, and INESSS, OurPATHS offers
          both analytical dashboards and a generative AI assistant. Together, these tools enable users
          to explore historical precedents, forecast pricing and approval timelines, and query data in
          natural language—all in one unified interface.
        </p>
      </div>

      {/* Eight foundational principles */}
      <div className="max-w-4xl mx-auto py-10 px-4 sm:px-8 lg:px-32">
        <h2 className="text-2xl font-semibold text-center mb-6">
          At its core, OurPATHS is built around eight foundational principles.
        </h2>
        <ul className="space-y-6 text-sm md:text-base">
          <li>
            <strong>Observational:</strong> Captures and structures real-world evidence from pCPA, CDA, and INESSS
            to support data-driven market access analysis.
          </li>
          <li>
            <strong>Usable:</strong> Designed with intuitive interfaces, from dashboard filters to natural language queries,
            to minimize friction for end-users.
          </li>
          <li>
            <strong>Real-time:</strong> Continuously updated to reflect evolving policy decisions, pricing outcomes,
            and approval timelines across jurisdictions.
          </li>
          <li>
            <strong>Predictive:</strong> Employs machine learning models to forecast likely pricing outcomes, approval durations,
            and negotiation trajectories.
          </li>
          <li>
            <strong>Actionable:</strong> Delivers strategic insights that inform HTA preparation, launch planning,
            and pricing submissions.
          </li>
          <li>
            <strong>Transparent:</strong> Visualizations and AI outputs are interpretable, with data sources clearly
            referenced for auditability and stakeholder trust.
          </li>
          <li>
            <strong>Holistic:</strong> Integrates diverse data sources and analytics to provide a 360-degree view
            of the market access landscape.
          </li>
          <li>
            <strong>Strategic:</strong> Built to empower pharmaceutical professionals with tools for scenario modeling,
            benchmarking, and proactive engagement with regulators.
          </li>
        </ul>
      </div>
    </div>
  );
};

export default About;