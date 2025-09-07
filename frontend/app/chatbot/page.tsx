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
  const { chats, setChats, currentChatId, setCurrentChatId } = useChat();

  // Load sessions on mount when user is available
  useEffect(() => {
    if (!user) return;
    let cancelled = false;

    (async () => {
      const res = await chatbotApi.listSessions(user.id);
      if (cancelled) return;

      if (res.data) {
        const serverChats = res.data.map((s) => ({
          id: s.id,
          title: s.chat_summary || `Chat ${s.id}`,
          messages: [],
        }));
        setChats(serverChats);
        if (serverChats.length > 0) {
          setCurrentChatId(serverChats[0].id);
        }
      } else if (res.error) {
        console.error("List sessions failed:", res.error);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user]);

  // Load messages when currentChatId changes
  useEffect(() => {
    if (!user || !currentChatId) return;
    let cancelled = false;

    (async () => {
      const res = await chatbotApi.getMessages(currentChatId, user.id);
      if (cancelled) return;

      if (res.data) {
        const msgs: ChatMessage[] = res.data.messages.map((m, idx) => ({
          id: `${currentChatId}:${idx}`,
          role: m.role.toLowerCase() === "assistant" ? "bot" : "user",
          text: m.content,
        }));
        setChats((prev) =>
          prev.map((c) => (c.id === currentChatId ? { ...c, messages: msgs } : c))
        );
      } else if (res.error) {
        console.error("Get messages failed:", res.error);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user, currentChatId]);

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar open={sidebarOpen} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <div className="flex flex-col justify-between flex-1 overflow-y-auto">
          <ChatWindow />
          <ChatInput />
        </div>
      </div>
    </div>
  );
}
