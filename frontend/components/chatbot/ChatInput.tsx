"use client";

import { useState } from "react";
import { useChat } from "./ChatContext";
import { v4 as uuidv4 } from "uuid";
import type { ChatMessage } from "./types";
import { Mic, Plus, Send } from "lucide-react"; 

export default function ChatInput() {
  const [input, setInput] = useState("");
  const { chats, setChats, currentChatId } = useChat();

  const currentChat = chats.find(c => c.id === currentChatId);
  const hasNoMsgs = currentChat?.messages.length === 0;
  const hasOnlyBot = currentChat?.messages.length === 1 &&
    currentChat.messages[0].role === "bot" 

  const showWelcomeHeading = hasNoMsgs || hasOnlyBot;

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
    <div className="w-full flex justify-center px-4 py-9 bg-[var(--main-body)] border-t-0">
      <div className="w-full max-w-4xl">
        {/* Welcome heading to show only if its the first message */}
        {/** TODO: Possible extension ideas: make a list of greetings and randomize them on each new chat opened. Add good morning/evening aka greeting based on user's time. Personalize greeting to username. */}
        {showWelcomeHeading && (
          <div className="w-full max-w-4xl mx-auto text-center mb-4">
            <h1 className="text-2xl md:text-3xl font-sans">How can we help today?</h1>
          </div>
        )}
        <div
          className="flex items-center w-full rounded-full px-6 py-4
            bg-[var(--input-bg)] gap-4
            shadow-[0_1px_3px_rgba(0,0,0,0.2),0_4px_6px_rgba(0,0,0,0.1)]
            dark:shadow-[0_0_0_1px_rgba(255,255,255,0.1),0_2px_4px_rgba(255,255,255,0.05),0_6px_12px_rgba(255,255,255,0.03)]"
        >
          {/* Add button for file upload */}
          <button
            title="Add"
            className="hover:opacity-80 transition-opacity"
            onClick={() => {}}
          >
            <Plus className="w-5 h-5 text-[var(--input-text)]" />
          </button>

          {/* Input area */}
          <input
            type="text"
            placeholder="Search drug submissions, timelines, or pricing..."
            className="flex-1 bg-transparent text-[var(--input-text)] placeholder:text-[var(--input-text)] placeholder:opacity-50 focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />

          {/* Mic for text to speech */}
          <button
            title="Voice"
            className="hover:opacity-80 transition-opacity"
            onClick={() => {}}
          >
            <Mic className="w-5 h-5 text-[var(--input-text)]" />
          </button>

          {/* Send button/alternative for pressing enter */}
          <button
            title="Send"
            className="hover:opacity-80 transition-opacity"
            onClick={handleSend}
          >
            <Send className="w-5 h-5 text-[var(--input-text)]" />
          </button>
        </div>
      </div>
    </div>
  );
}
