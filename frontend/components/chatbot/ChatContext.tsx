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
// Comment for extension: Something we should think about is do we want to be receiving all the chats and 
// their information at once and have them stored on the client or should we have it be dynamically fetched 
// each time a particular chat history is clicked on. The way the backend is setup is aiming to support the 
// latter (mainly because if chat histories get very bulky, it can be inefficient time- and space-wise to get 
// all the messages for all the chats for a user), but the frontend client can call the backend for each 
// individual chat here and receive all the chats before loading the page in the first place, which would 
// support the former functionality (which is how your mock is setup right now).
// Something to be aware of when we connect the backend to the frontend for this part.
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
