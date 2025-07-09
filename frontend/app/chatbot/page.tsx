"use client";

import { useState } from "react";
import Sidebar from "@/components/chatbot/Sidebar";
import Topbar from "@/components/chatbot/Topbar";
import ChatWindow from "@/components/chatbot/ChatWindow";
import ChatInput from "@/components/chatbot/ChatInput";

export default function ChatbotPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} />

      {/* Main area (Topbar + ChatWindow + ChatInput) */}
      <div className="flex flex-col flex-1">
        <Topbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

        {/* Chat content area */}
        <div className="flex flex-col justify-between flex-1 overflow-y-auto">
          <ChatWindow />
          <ChatInput />
        </div>
      </div>
    </div>
  );
}
