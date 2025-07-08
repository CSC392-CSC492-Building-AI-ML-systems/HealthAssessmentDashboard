import { useChat } from "./ChatContext";
import MessageBubble from "./MessageBubble";

export default function ChatWindow() {
  const { chats, currentChatId } = useChat();
  const currentChat = chats.find((c) => c.id === currentChatId);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[var(--background)] text-[var(--foreground)]">
      {currentChat?.messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
}
