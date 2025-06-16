"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Accordion from "./Accordion"

const dataFAQ = [
        {question: "What insurance companies or health sites are used in the training of the chatbot?",
            answer: "We have utilized information from multiple sites, including pCPA, CDA, and INESSS.",},

        {question: "What is the cost of using the OurPATHS AI-assisstant?",
            answer: "Our chatbot and dashboard are completely free for usage! You can get started by creating an account here.",},

        {question: "Where can I report issues or bugs?",
            answer: "You can contact us at contact@ourpaths.ca for any spotted issues!",},
]
const FAQ: React.FC = () => {
    return (
        <div>
          <h1 className = "pt-10 pb-12 text-center text-5xl lg:text-6xl font-semibold tracking-wide"
          style={{ color: 'var(--brand-dark)' }}>
            FAQ
            </h1>

          {dataFAQ.map((data, i) => <div key={i}>
                <Accordion
                    question={data.question}
                    answer={data.answer}/>
          </div>)}
        </div>
      );
    };

export default FAQ;