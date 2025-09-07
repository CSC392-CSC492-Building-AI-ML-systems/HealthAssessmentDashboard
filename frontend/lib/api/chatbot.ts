import { httpClient } from './core/http-client';
import {
  ApiResponse,
  ChatMessage,
  ChatHistory,
} from './types';

/**
 * Chatbot-related API endpoints
 */
export const chatbotApi = {
  /**
   * Create a chat session on the server
   */
  createSession: async (
    userId: number,
    title: string
  ): Promise<ApiResponse<{ id: number; chat_summary: string }>> => {
    const fd = new FormData();
    fd.append("user_id", String(userId));
    fd.append("title", title);
    return httpClient(`/chat/sessions`, {
      method: "POST",
      body: fd,
    });
  },

  /**
   * List sessions for a user
   */
  listSessions: async (
    userId: number
  ): Promise<ApiResponse<Array<any>>> => {
    return httpClient(`/chat/sessions?user_id=${encodeURIComponent(String(userId))}`);
  },

  /**
   * Get all messages for a session
   */
  getMessages: async (
    sessionId: number,
    userId: number
  ): Promise<ApiResponse<{ messages: Array<{ role: string; content: string }> }>> => {
    return httpClient(
      `/chat/sessions/${sessionId}/messages?user_id=${encodeURIComponent(String(userId))}`
    );
  },

  /**
   * Send a message to the chatbot
   * Uses FormData because the backend endpoint reads Form(...) inputs
   */
  sendMessage: async (
    sessionId: string,
    userId: string,
    message: string
  ): Promise<ApiResponse<ChatMessage>> => {
    const fd = new FormData();
    fd.append("user_id", userId);
    fd.append("message", message);
    return httpClient<ChatMessage>(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: fd,
    });
  },

  renameChat: async (sessionId: number, userId: number, newTitle: string) => {
    const formData = new FormData();
    formData.append("user_id", String(userId));
    formData.append("new_title", newTitle);
    return httpClient(`/chat/sessions/${sessionId}`, {
      method: "PUT",
      body: formData,
    });
  },

  getChatHistory: async (): Promise<ApiResponse<ChatHistory>> => {
    return httpClient<ChatHistory>("/chatbot/history");
  },

  clearChatHistory: async (): Promise<ApiResponse<void>> => {
    return httpClient<void>("/chatbot/history", { method: "DELETE" });
  },

  getConversation: async (conversationId: string): Promise<ApiResponse<ChatHistory>> => {
    return httpClient<ChatHistory>(`/chatbot/conversations/${conversationId}`);
  },
};
