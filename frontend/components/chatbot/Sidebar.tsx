// TODO: replace report bug button link with real email address/modal to real email address.
import { useChat } from "./ChatContext";

export default function Sidebar() {
    // pull shared state from context
    const { chats, setChats, currentChatId, setCurrentChatId } = useChat();

    // create a new session
    const handleNewChat = () => {
        const nextId = chats.length + 1;
        const newChat = { id: nextId, title: `New Chat ${nextId}`, messages: [] };
        setChats([newChat, ...chats]);
        setCurrentChatId(nextId);
    };

    // visually render sidebar layout, title, new chats, and report bug at the bottom
    return (
        <aside className="w-64 bg-[var(--brand-dark)] text-[var(--text-light)] p-4 flex flex-col justify-between">
        <div>
            <h1 className="text-xl font-semibold mb-6">OurPATHS</h1>
            <button onClick={handleNewChat} className="mb-4 w-full text-left">
                ➕ New Chat
            </button>
            <ul className="space-y-2">
            {chats.map((chat) => (
                <li key={chat.id}>
                <button
                    className={`w-full text-left rounded px-2 py-1 ${
                    chat.id === currentChatId ? "bg-gray-700" : "hover:bg-gray-800"
                    }`}
                    onClick={() => setCurrentChatId(chat.id)}
                >
                    {chat.title}
                </button>
                </li>
            ))}
         </ul>
        </div>
        <a
            href="mailto:placeholder@ourpaths.com?subject=Bug Report&body=Describe your issue here..."
            className="text-sm text-blue-400 hover:underline"
        >
            Report Bug
        </a>
        </aside>
    );
    }   
