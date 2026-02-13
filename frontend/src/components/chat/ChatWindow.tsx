'use client';

import { useEffect, useRef } from 'react';
import { useChatStore, useTaskStore } from '@/lib/stores';
import ChatInput from './ChatInput';
import MessageBubble from './MessageBubble';
import ThinkingIndicator from './ThinkingIndicator';
import { NoChatEmpty } from '@/components/ui/EmptyState';

interface ChatWindowProps {
  projectId: string;
}

export default function ChatWindow({ projectId }: ChatWindowProps) {
  const { messages, isLoading, isSending, error, fetchHistory, sendMessageStreaming, clearHistory, clearError } = useChatStore();
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
      const response = await sendMessageStreaming(content);
      // Refresh tasks if agent used any task-mutating tools
      const TASK_MUTATING_TOOLS = ['create_task', 'bulk_create_tasks', 'confirm_proposed_tasks', 'update_task', 'delete_task', 'confirm_plan'];
      if (response?.tool_calls?.some((tc) => TASK_MUTATING_TOOLS.includes(tc.tool_name))) {
        await fetchTasks();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border">
      <div className="px-4 py-4 border-b bg-gradient-to-r from-blue-50 to-white flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">AI Assistant</h2>
          <p className="text-sm text-gray-700 mt-1">Search docs, create tasks, manage your project</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            disabled={isSending}
            className="text-xs text-gray-400 hover:text-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-1"
            title="Clear chat history"
          >
            Clear chat
          </button>
        )}
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
          <NoChatEmpty />
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isSending && <ThinkingIndicator />}
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
