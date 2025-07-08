"use client";

import { useState } from "react";
import { useChat } from "./ChatContext";
import { v4 as uuidv4 } from "uuid";
import type { ChatMessage } from "./types";

export default function ChatInput() {
  const [input, setInput] = useState("");
  const { chats, setChats, currentChatId } = useChat();

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: "user",
      text: trimmed,
    };

    const botMessage: ChatMessage = {
      id: uuidv4(),
      role: "bot",
      text: "Thanks for your message! This is a dummy response.",
    };

    const updatedChats = chats.map((chat) => {
      if (chat.id !== currentChatId) return chat;
      return {
        ...chat,
        messages: [...chat.messages, userMessage, botMessage],
      };
    });

    setChats(updatedChats);
    setInput("");
  };

  return (
    <div className="flex items-center gap-3 px-6 py-4 bg-[var(--background)] border-t border-[var(--feature-bg)]">
      {/* TO BE REPLACED: Attachment icon */}
      <button title="Attach file" className="text-xl">
        ➕
      </button>

      {/* TO BE REPLACED: Mic icon */}
      <button title="Speech-to-text" className="text-xl">
        🎤
      </button>

      {/* Input field */}
      <input
        type="text"
        placeholder="Type your message..."
        className="flex-1 px-4 py-2 rounded bg-white text-[var(--brand-dark)] focus:outline-none"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
      />
    </div>
  );
}
