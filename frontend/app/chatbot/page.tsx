"use client";

import { ChatProvider } from "@/components/chatbot/ChatContext";
import Sidebar from "@/components/chatbot/Sidebar";
import Topbar from "@/components/chatbot/Topbar";
import ChatWindow from "@/components/chatbot/ChatWindow";
import ChatInput from "@/components/chatbot/ChatInput";

export default function ChatbotPage() {
  return (
    <ChatProvider>
      <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Area */}
        <div className="flex flex-col flex-1">
          <Topbar />
          <ChatWindow />
          <ChatInput />
        </div>
      </div>
    </ChatProvider>
  );
}
