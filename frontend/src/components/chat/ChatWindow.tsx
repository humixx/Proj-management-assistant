'use client';

import { useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ThinkingIndicator from './ThinkingIndicator';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatWindowProps {
  projectId: string;
  initialMessages?: Message[];
}

export default function ChatWindow({ projectId, initialMessages = [] }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // TODO: Send to backend API
      // const response = await fetch(`/api/projects/${projectId}/chat`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ message: content }),
      // });
      // const data = await response.json();
      
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // For now, just echo back (remove when API is ready)
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a placeholder response. Connect to your backend API to get real responses.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      // TODO: Show error message to user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
      {/* Chat Header */}
      <div className="bg-white rounded-t-lg border border-gray-200 border-b-0 p-4">
        <h2 className="text-xl font-bold text-gray-900">Project Chat</h2>
        <p className="text-sm text-gray-700">Project ID: {projectId}</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-white border-x border-gray-200 overflow-y-auto p-6">
        <MessageList messages={messages} />
        {isLoading && <ThinkingIndicator />}
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
