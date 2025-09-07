"use client";

import { useState, useEffect } from "react";
import { useChat } from "./ChatContext";
import { Menu, SquarePen, Bug, Pencil } from "lucide-react";
import { v4 as uuidv4 } from "uuid";
import { ChatMessage, ChatSession } from "./types";
import { chatbotApi } from "@/lib/api/chatbot";
import { useAuth } from "@/hooks/useAuth";

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { chats, setChats, currentChatId, setCurrentChatId } = useChat();
  const [editingChatId, setEditingChatId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const { user } = useAuth();

  useEffect(() => {
    if (chats.length === 0) {
      const newChat: ChatSession = {
        id: 1,
        title: "New Chat 1",
        messages: [], // no messages on first load
      };

      setChats([newChat]);
      setCurrentChatId(1);
    }
  }, []);

  const handleNewChat = () => {
    const nextId = chats.length + 1;
    const newChat: ChatSession = {
      id: nextId,
      title: `New Chat ${nextId}`,
      messages: [],
    };

    setChats([newChat, ...chats]);
    setCurrentChatId(nextId);
  };

  const handleRename = (id: number, newTitle: string) => {
    const updatedChats = chats.map((chat) =>
      chat.id === id ? { ...chat, title: newTitle.trim() || chat.title } : chat
    );
    setChats(updatedChats);

    if (user) {
      chatbotApi.renameChat(id, user.id, newTitle).catch((err) =>
        console.error("Rename failed", err)
      );
    }
  };

  return (
    <aside
      className={`transition-all duration-300 ease-in-out
        bg-[var(--bars)] text-[var(--text-light)]
        h-screen flex flex-col justify-between p-4
        ${collapsed ? "w-[60px] items-center" : "w-[250px]"}
        ${open ? "" : "hidden"}
        shadow-[2px_0_8px_rgba(0,0,0,0.15)]`}
    >
      <div className={`space-y-4 w-full`}>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={`hover:bg-[var(--hover-box)] p-2 rounded-xl w-full ${
            collapsed ? "flex justify-center items-center" : ""
          }`}
        >
          <Menu className="w-6 h-6 shrink-0" />
        </button>

        <button
          onClick={handleNewChat}
          className={`text-sm hover:bg-[var(--hover-box)] rounded-xl p-2 w-full ${
            collapsed ? "flex justify-center items-center" : "flex items-center gap-2"
          }`}
        >
          <SquarePen className="w-5 h-5 shrink-0" />
          {!collapsed && <span className="whitespace-nowrap">New Chat</span>}
        </button>

        {!collapsed && <hr className="border-t border-[var(--hover-box)]" />}

        {!collapsed && (
          <ul className="space-y-2 pt-2 max-h-[60vh] overflow-y-auto">
            {chats.map((chat) => (
              <li key={chat.id} className="group">
                <div
                  onClick={() => setCurrentChatId(chat.id)}
                  className={`w-full text-left text-sm rounded-xl px-2 py-2 transition-colors flex justify-between items-center ${
                    chat.id === currentChatId ? "bg-[var(--hover-box)]" : "hover:bg-[var(--hover-box)]"
                  }`}
                >
                  {editingChatId === chat.id ? (
                    <input
                      autoFocus
                      className="bg-transparent border-b border-white text-sm focus:outline-none w-full"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onBlur={() => {
                        handleRename(chat.id, editTitle);
                        setEditingChatId(null);
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleRename(chat.id, editTitle);
                          setEditingChatId(null);
                        } else if (e.key === "Escape") {
                          setEditingChatId(null);
                        }
                      }}
                    />
                  ) : (
                    <div className="flex items-center justify-between w-full">
                      <span
                        className="whitespace-nowrap overflow-hidden text-ellipsis pr-2 w-full"
                        onDoubleClick={(e) => {
                          e.stopPropagation();
                          setEditingChatId(chat.id);
                          setEditTitle(chat.title);
                        }}
                      >
                        {chat.title}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingChatId(chat.id);
                          setEditTitle(chat.title);
                        }}
                        className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 text-gray-400 hover:text-white"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className={`${collapsed ? "flex justify-center" : ""}`}>
        {!collapsed && <hr className="border-t border-[var(--hover-box)] mb-2 w-full" />}

        <a
          href="mailto:placeholder@ourpaths.com?subject=Bug Report&body=Describe your issue here..."
          className={`text-sm p-2 rounded-xl transition-colors w-full
            hover:text-[var(--text-onhover-red)]
            ${collapsed ? "flex justify-center items-center" : "flex items-center gap-2"}`}
        >
          <Bug className="w-5 h-5 shrink-0" />
          {!collapsed && <span className="whitespace-nowrap">Report Bug</span>}
        </a>
      </div>
    </aside>
  );
}
