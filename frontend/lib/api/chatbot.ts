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
   * Send a message to the chatbot
   */
  sendMessage: async (message: string): Promise<ApiResponse<ChatMessage>> => {
    return httpClient<ChatMessage>('/chatbot/message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },

  /**
   * Get chat history
   */
  getChatHistory: async (): Promise<ApiResponse<ChatHistory>> => {
    return httpClient<ChatHistory>('/chatbot/history');
  },

  /**
   * Clear chat history
   */
  clearChatHistory: async (): Promise<ApiResponse<void>> => {
    return httpClient<void>('/chatbot/history', {
      method: 'DELETE',
    });
  },

  /**
   * Get conversation by ID
   */
  getConversation: async (conversationId: string): Promise<ApiResponse<ChatHistory>> => {
    return httpClient<ChatHistory>(`/chatbot/conversations/${conversationId}`);
  },
};
