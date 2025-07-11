"use client";
import { useChat } from "./ChatContext";
import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";

export default function ChatWindow() {
  const { chats, currentChatId } = useChat();
  const currentChat = chats.find((c) => c.id === currentChatId);

  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll when user sends new messsage
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [currentChat?.messages.length]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6 bg-[var(--main-body)] text-[var(--foreground)] flex justify-center"
    >
      <div className="w-full max-w-5xl space-y-4 pb-12">
        {currentChat?.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Buffer for spacing */}
        <div className="h-8" />

        {/* Anchor for scroll */}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
