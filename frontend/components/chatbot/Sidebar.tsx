// TODO: replace report bug button link with real email address/modal to real email address. 
"use client";

import { useState } from "react";
import { useChat } from "./ChatContext";
import { Menu, Plus, Bug } from "lucide-react";

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
    const [collapsed, setCollapsed] = useState(false);
    const { chats, setChats, currentChatId, setCurrentChatId } = useChat();

    const handleNewChat = () => {
        const nextId = chats.length + 1;
        const newChat = {
        id: nextId,
        title: `New Chat ${nextId}`,
        messages: [],
        };
        setChats([newChat, ...chats]);
        setCurrentChatId(nextId);
    };

    return (
        <aside
        className={`transition-all duration-300 ease-in-out bg-[var(--brand-dark)] text-[var(--text-light)] 
        h-screen flex flex-col justify-between p-4 shadow-lg
        ${collapsed ? "w-[60px]" : "w-[250px]"}`}
        >
        {/* Top Section */}
        <div className="space-y-4">
            {/* Toggle Button */}
            <button
            onClick={() => setCollapsed(!collapsed)}
            className="text-[var(--text-light)] hover:opacity-70"
            >
            <Menu className="w-6 h-6" />
            </button>

            {/* New Chat */}
            <button
            onClick={handleNewChat}
            className="flex items-center gap-2 text-sm hover:opacity-80"
            >
            <Plus className="w-5 h-5" />
            {!collapsed && <span>New Chat</span>}
            </button>

            {/* Chat Sessions */}
            {!collapsed && (
            <ul className="space-y-2 pt-4">
                {chats.map((chat) => (
                <li key={chat.id}>
                    <button
                    className={`w-full text-left text-sm rounded px-2 py-1 ${
                        chat.id === currentChatId
                        ? "bg-gray-700"
                        : "hover:bg-gray-800"
                    }`}
                    onClick={() => setCurrentChatId(chat.id)}
                    >
                    {chat.title}
                    </button>
                </li>
                ))}
            </ul>
            )}
        </div>

        {/* Report Bug Button */}
        <a
            href="mailto:placeholder@ourpaths.com?subject=Bug Report&body=Describe your issue here..."
            className="text-sm flex items-center gap-2 hover:underline"
        >
            <Bug className="w-4 h-4" />
            {!collapsed && <span>Report Bug</span>}
        </a>
        </aside>
    );
    }
