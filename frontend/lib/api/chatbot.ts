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
  sendMessage: async (
    sessionId: string,
    userId: string,
    message: string
  ): Promise<ApiResponse<ChatMessage>> => {
    console.log("Sending message to chatbot:", {
      sessionId, userId, message
    });
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("message", message);
    
    // Log FormData content
    for (let pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
    }
    console.log("Sending message to chatbot:", {
      user_id: userId,
      message: message
    });
    return httpClient<ChatMessage>(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, message }),
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
