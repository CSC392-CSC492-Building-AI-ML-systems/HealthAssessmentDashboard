"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { ArrowUp, ArrowDown } from 'lucide-react';
type AccordionProps = {
  question: string,
  answer: string,
} 
const Accordion = (props: AccordionProps) => {
  const [showQA, setShowQA] = useState(false);

    return (
        <div className = "py-4 px-3 my-6 max-w-2xl mx-auto flex flex-col gap-6">
          <button
            className = "flex flex-row items-center justify-between text-left gap-4 font-semibold"
            onClick={() => setShowQA(!showQA)}
          >
            <span className = "text-lg">
              {props.question} 
            </span>
            <span style={{ color: 'var(--brand-light)' }}>
              {showQA ? <ArrowUp /> : <ArrowDown />}
            </span>
          </button>
          {showQA && <p className = "text-md">
            {props.answer}
          </p>}
        </div>
      );
    };

export default Accordion;