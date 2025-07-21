// TODO: replace report bug button link with real email address/modal to real email address. 
// TODO: add a shadow to the right/ fix the code below:
//             shadow-[10px_0_20px_rgba(0,0,0,0.4)] dark:shadow-[2px_0_8px_rgba(255,255,255,0.05)]`}

"use client";

import { useState } from "react";
import { useChat } from "./ChatContext";
import { Menu, SquarePen, Bug } from "lucide-react";
import { v4 as uuidv4 } from "uuid";
import { ChatMessage, ChatSession } from "./types";
import { useEffect } from "react";


interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
    const [collapsed, setCollapsed] = useState(false);
    const { chats, setChats, currentChatId, setCurrentChatId } = useChat();


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

  return (
    <aside
      className={`transition-all duration-300 ease-in-out
        bg-[var(--bars)] text-[var(--text-light)]
        h-screen flex flex-col justify-between p-4
        ${collapsed ? "w-[60px] items-center" : "w-[250px]"}
        ${open ? "" : "hidden"}
        shadow-[2px_0_8px_rgba(0,0,0,0.15)]`}
    >
      {/* Top Section */}
      <div className={`space-y-4 w-full`}>
        {/* Toggle Button */}
        <button
            onClick={() => setCollapsed(!collapsed)}
            className={`hover:bg-[var(--hover-box)] p-2 rounded-xl w-full
                ${collapsed ? "flex justify-center items-center" : ""}`}
            >
            <Menu className="w-6 h-6 shrink-0" />
        </button>

        {/* New Chat */}
        <button
            onClick={handleNewChat}
            className={`text-sm hover:bg-[var(--hover-box)] rounded-xl p-2 w-full
                ${collapsed ? "flex justify-center items-center" : "flex items-center gap-2"}`}
            >
            <SquarePen className="w-5 h-5 shrink-0" />
            {!collapsed && <span className="whitespace-nowrap">New Chat</span>}
        </button>

        {/* Divider */}
        {!collapsed && (
          <hr className="border-t border-[var(--hover-box)]" />
        )}

        {/* Chat Sessions */}
        {!collapsed && (
          <ul className="space-y-2 pt-2 max-h-[60vh] overflow-y-auto">
            {chats.map((chat) => (
              <li key={chat.id}>
                <button
                  onClick={() => setCurrentChatId(chat.id)}
                  className={`w-full text-left text-sm rounded-xl px-2 py-2 transition-colors flex
                    ${
                      chat.id === currentChatId
                        ? "bg-[var(--hover-box)]"
                        : "hover:bg-[var(--hover-box)]"
                    }`}
                >
                  {chat.title}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

        {/* Bottom Section */}
        <div className={`${collapsed ? "flex justify-center" : ""}`}>
        {/* Divider - Only visible when not collapsed */}
        {!collapsed && (
            <hr className="border-t border-[var(--hover-box)] mb-2 w-full" />
        )}

        {/* Report Bug */}
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
