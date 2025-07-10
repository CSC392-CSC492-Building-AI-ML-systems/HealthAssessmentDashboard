// import { useEffect, useRef } from "react";
// import { useChat } from "./ChatContext";
// import MessageBubble from "./MessageBubble";

// export default function ChatWindow() {
//   const { chats, currentChatId } = useChat();
//   const currentChat = chats.find((c) => c.id === currentChatId);
//   const containerRef = useRef<HTMLDivElement | null>(null);
//   const bottomRef = useRef<HTMLDivElement | null>(null);

//   useEffect(() => {
//     if (bottomRef.current && containerRef.current) {
//       containerRef.current.scrollTo({
//         top: bottomRef.current.offsetTop,
//         behavior: "smooth",
//       });
//     }
//   }, [currentChat?.messages.length]);

//   return (
//     <div
//       ref={containerRef}
//       className="flex-1 overflow-y-auto px-4 pt-6 bg-[var(--main-body)] text-[var(--foreground)] flex justify-center"
//     >
//       <div className="w-full max-w-5xl space-y-2">
//         {currentChat?.messages.map((message) => (
//           <MessageBubble key={message.id} message={message} />
//         ))}

//         {/* Div to avoid overlap with chat input/keep some spacing for readability */}
//         <div className="h-6" />

//         {/* Scroll anchor */}
//         <div ref={bottomRef} />
//       </div>
//     </div>
//   );
// }

"use client";
import { useChat } from "./ChatContext";
import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";

export default function ChatWindow() {
  const { chats, currentChatId } = useChat();
  const currentChat = chats.find((c) => c.id === currentChatId);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll ONLY when overflow happens (i.e., new chat message)
  useEffect(() => {
    if (!scrollRef.current) return;

    const el = scrollRef.current;
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100;

    if (isAtBottom) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [currentChat?.messages.length]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6 bg-[var(--main-body)] text-[var(--foreground)] flex justify-center"
    >
      <div className="w-full max-w-5xl space-y-4 pb-12">
        {currentChat?.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </div>
  );
}
