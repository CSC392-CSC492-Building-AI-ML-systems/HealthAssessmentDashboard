// Setting up a React Context to handle messages and shared info.
"use client";
import { createContext, useContext, useState, ReactNode } from "react";
import { ChatSession } from "./types";

type ChatContextType = {
  chats: ChatSession[];
  setChats: React.Dispatch<React.SetStateAction<ChatSession[]>>;
  currentChatId: number | null;
  setCurrentChatId: React.Dispatch<React.SetStateAction<number | null>>;
  showWelcome: boolean;
  setShowWelcome: React.Dispatch<React.SetStateAction<boolean>>;
};

const ChatContext = createContext<ChatContextType | null>(null);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [showWelcome, setShowWelcome] = useState(true);

  return (
    <ChatContext.Provider
      value={{
        chats,
        setChats,
        currentChatId,
        setCurrentChatId,
        showWelcome,
        setShowWelcome,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};


// instead of useContext(ChatContext), we can just call useChat()
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within ChatProvider");
  return context;
};
