"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

const Summary: React.FC = () => {
    return (
    <section className="bg-[var(--foreground)] text-[var(--background)] py-16 px-4 sm:px-8 lg:px-32">
      <div className="max-w-5xl mx-auto text-center">
        <p className="text-lg sm:text-xl leading-relaxed font-body">
          The <strong>Observational, Usable & Real-time Predictive Analytics Toolkit for Healthcare Strategy (OurPATHS)</strong> platform is a predictive analytics toolkit powered by machine learning and generative AI, enabling smarter, faster, and more strategic drug/medical-device pricing and reimbursement submissions.
        </p>
      </div>
    </section>
  );
}

export default Summary;