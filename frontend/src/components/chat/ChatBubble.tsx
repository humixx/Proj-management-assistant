'use client';

import { useState, useEffect, useRef } from 'react';
import { useChatStore, useTaskStore } from '@/lib/stores';
import ChatInput from './ChatInput';
import MessageBubble from './MessageBubble';
import ThinkingIndicator from './ThinkingIndicator';

interface ChatBubbleProps {
  projectId: string;
}

export default function ChatBubble({ projectId }: ChatBubbleProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, isSending, error, fetchHistory, sendMessageStreaming, clearError } = useChatStore();
  const { fetchTasks } = useTaskStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [hasLoaded, setHasLoaded] = useState(false);

  // Load history when panel first opens
  useEffect(() => {
    if (isOpen && !hasLoaded) {
      fetchHistory();
      setHasLoaded(true);
    }
  }, [isOpen, hasLoaded, fetchHistory]);

  // Auto-scroll on new messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isSending, isOpen]);

  // Auto-dismiss errors
  useEffect(() => {
    if (error) {
      const timer = setTimeout(clearError, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleSendMessage = async (content: string) => {
    try {
      const response = await sendMessageStreaming(content);
      const TASK_MUTATING_TOOLS = ['create_task', 'bulk_create_tasks', 'confirm_proposed_tasks', 'update_task', 'delete_task'];
      if (response?.tool_calls?.some((tc) => TASK_MUTATING_TOOLS.includes(tc.tool_name))) {
        await fetchTasks();
      }
    } catch (err) {
      console.error('Chat bubble error:', err);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
          isOpen
            ? 'bg-gray-700 hover:bg-gray-800 rotate-0'
            : 'bg-blue-600 hover:bg-blue-700 hover:scale-105'
        }`}
      >
        {isOpen ? (
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )}
        {!isOpen && isSending && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-orange-500"></span>
          </span>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[520px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden animate-in">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold">AI Assistant</h3>
                <p className="text-xs text-blue-100">Create tasks, ask questions</p>
              </div>
            </div>
          </div>

          {/* Error bar */}
          {error && (
            <div className="px-3 py-1.5 bg-red-50 dark:bg-red-900/30 border-b border-red-200 dark:border-red-800 flex justify-between items-center flex-shrink-0">
              <span className="text-xs text-red-700 dark:text-red-300">{error}</span>
              <button onClick={clearError} className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300">Dismiss</button>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.length === 0 && !isSending ? (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center mb-3">
                  <svg className="w-6 h-6 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">How can I help?</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Ask me to create tasks or manage your project</p>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                {isSending && <ThinkingIndicator />}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-3 flex-shrink-0">
            <ChatInput onSend={handleSendMessage} disabled={isSending} />
          </div>
        </div>
      )}
    </>
  );
}
