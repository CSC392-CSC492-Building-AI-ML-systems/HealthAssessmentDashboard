// Setting up a React Context to handle messages and shared info.
"use client";
import { createContext, useContext, useState, ReactNode } from "react";
import { ChatSession } from "./types";

type ChatContextType = {
  chats: ChatSession[]; //array of chats aka chat history
  setChats: React.Dispatch<React.SetStateAction<ChatSession[]>>; // function to update chats
  currentChatId: number; // open chat's ID
  setCurrentChatId: React.Dispatch<React.SetStateAction<number>>; // function to update which chat is open
};

// create the actual react context object
const ChatContext = createContext<ChatContextType | null>(null);

// wrapper
export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [chats, setChats] = useState<ChatSession[]>([
    { id: 1, title: "New Chat 1", messages: [] },
  ]);
  const [currentChatId, setCurrentChatId] = useState(1);

  // context to children to wrap all child components
  return (
    <ChatContext.Provider value={{ chats, setChats, currentChatId, setCurrentChatId }}>
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
