"use client";

import { useState, useEffect } from "react";
import Sidebar from "@/components/chatbot/Sidebar";
import Topbar from "@/components/chatbot/Topbar";
import ChatWindow from "@/components/chatbot/ChatWindow";
import ChatInput from "@/components/chatbot/ChatInput";
import { useAuth } from "@/hooks/useAuth";
import { useChat } from "@/components/chatbot/ChatContext";
import { chatbotApi } from "@/lib/api/chatbot";
import type { ChatMessage } from "@/components/chatbot/types";

export default function ChatbotPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user } = useAuth();
  const { chats, setChats, currentChatId, setCurrentChatId, showWelcome } = useChat();

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        open={sidebarOpen}
      />
      <div className="flex flex-col flex-1 overflow-hidden">
        <div className="flex flex-col justify-between flex-1 overflow-y-auto">
          {showWelcome ? (
            <div className="flex flex-1 flex-col items-center justify-center text-center p-4">
              <h1 className="text-3xl font-bold mb-2">Welcome</h1>
              <p className="text-lg text-gray-600">
                Click on an existing chat or create a new chat to get started!
              </p>
            </div>
          ) : (
            <>
              <ChatWindow />
              <ChatInput />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
