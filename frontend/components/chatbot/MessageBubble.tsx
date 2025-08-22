// import type definitions for messages
"use client";
import { ChatMessage } from "./types";
import { useEffect, useState } from "react";

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  // TODO: FIX TYPING ANIMATION (enhancement for later)
  // const [displayedText, setDisplayedText] = useState(
  //   isUser ? message.text : ""
  // );

  // useEffect(() => {
  //   if (!isUser && message.text) {
  //     let index = 0;
  //     const interval = setInterval(() => {
  //       setDisplayedText((prev) => message.text.slice(0, index + 1));
  //       index++;

  //       if (index >= message.text.length) {
  //         clearInterval(interval);
  //       }
  //     }, 25);

  //     return () => clearInterval(interval);
  //   }
  // }, [isUser, message.text]);

  const displayedText = message.text;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] px-4 py-2 rounded-2xl text-sm md:text-base leading-relaxed 
          ${isUser
            ? "bg-[var(--text-light)] text-[var(--hover-box)]"
            : "text-[var(--text-light)]" 
          } whitespace-pre-wrap`}
      >
        {displayedText}
      </div>
    </div>
  );
}
