"use client";

import { ChatProvider } from "@/components/chatbot/ChatContext";
import { LightDarkProvider } from "@/components/general/theme/LightDarkProvider";

export default function ChatbotLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LightDarkProvider>
      <ChatProvider>
        <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)]">
          {children}
        </div>
      </ChatProvider>
    </LightDarkProvider>
  );
}
