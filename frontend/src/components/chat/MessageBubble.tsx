'use client';

import { LocalMessage } from '@/types';

interface MessageBubbleProps {
  message: LocalMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-3 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
        <div className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</div>

        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.tool_calls.map((tc, i) => (
              <div key={i} className="bg-white rounded p-2 text-xs text-gray-700 border">
                <span className="font-semibold">{tc.tool_name}</span>
                {tc.result?.message && <span className="ml-2 text-gray-600">{tc.result.message}</span>}
              </div>
            ))}
          </div>
        )}

        <div className={`text-xs mt-2 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
