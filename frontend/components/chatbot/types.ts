// Defining shared types across the chatbot.
//1: Chatmessage: contains a unique ID, role to show who sent the message, text to show what was said, and timestamp to show when.
export type ChatMessage = {
  id: string;
  role: "user" | "bot";
  text: string;
  timestamp?: string;
};

//1: Chatsession: contains a unique ID , title/topic of discussion (aka chat number 1, 2, ...), and a list of all the messages in the chat.
export type ChatSession = {
  id: number;
  title: string;
  messages: ChatMessage[];
};
