// import type definitions for messages
import { ChatMessage } from "./types";

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] px-4 py-2 rounded-lg text-sm md:text-base leading-snug ${
          isUser
            ? "bg-[var(--brand-light)] text-[var(--brand-dark)]"
            : "bg-[var(--feature-bg)] text-[var(--brand-dark)]"
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
