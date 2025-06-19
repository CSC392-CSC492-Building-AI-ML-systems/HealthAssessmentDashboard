"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Accordion from "./Accordion"

/* Questions and answers that will be disaplyed */
/* TODO: possibly alter a few questions to be more detailed in terms of pharamceutical companies' concerns */
const dataFAQ = [
        {question: "What insurance companies or health sites are used in the training of the chatbot?",
            answer: "We have utilized information from multiple sites, including pCPA, CDA, and INESSS.",},

        {question: "Are the OurPATHS AI-assisstant and Dashboard free to use?",
            answer: "Our chatbot and dashboard are completely free for usage! You can get started by creating an account here.",},

        {question: "Where can I report issues or bugs?",
            answer: "You can contact us at contact@ourpaths.ca for any spotted issues!",},
]
/* Currently: Dark Mode */
const FAQ: React.FC = () => {
    return (
        <div>
          <h1 className = "pt-24 pb-8 text-center text-5xl lg:text-6xl font-semibold tracking-wide"
          style={{ color: 'var(--brand-light)' }}>
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