'use client';

import { useEffect, useRef } from 'react';
import { useChatStore, useTaskStore } from '@/lib/stores';
import ChatInput from './ChatInput';
import MessageBubble from './MessageBubble';

interface ChatWindowProps {
  projectId: string;
}

export default function ChatWindow({ projectId }: ChatWindowProps) {
  const { messages, isLoading, isSending, error, fetchHistory, sendMessage, clearError } = useChatStore();
  const { fetchTasks } = useTaskStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchHistory();
  }, [projectId, fetchHistory]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  // Auto-dismiss errors after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleSendMessage = async (content: string) => {
    try {
      const response = await sendMessage(content);
      // Refresh tasks if agent used task tools
      if (response?.tool_calls?.some((tc) => ['create_task', 'bulk_create_tasks'].includes(tc.tool_name))) {
        await fetchTasks();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Error is already handled in the store
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border">
      <div className="px-4 py-4 border-b bg-gradient-to-r from-blue-50 to-white">
        <h2 className="text-xl font-bold text-gray-900">AI Assistant</h2>
        <p className="text-sm text-gray-700 mt-1">Search docs, create tasks, manage your project</p>
      </div>

      {error && (
        <div className="px-4 py-2 bg-red-50 border-b border-red-200 flex justify-between items-center">
          <span className="text-sm text-red-700 font-medium">{error}</span>
          <button onClick={clearError} className="text-sm text-red-600 hover:text-red-800 font-medium">Dismiss</button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="text-center text-gray-600 font-medium">Loading...</div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-xl font-semibold text-gray-700 mb-2">Start a conversation</p>
            <p className="text-base">Upload documents and ask me to analyze them or create tasks</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-3 text-gray-700 font-medium">Thinking...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="border-t p-4">
        <ChatInput onSend={handleSendMessage} disabled={isSending} />
      </div>
    </div>
  );
}
