'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownContentProps {
  content: string;
  isUser?: boolean;
}

export default function MarkdownContent({ content, isUser = false }: MarkdownContentProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        strong: ({ children }) => (
          <strong className={`font-semibold ${isUser ? 'text-white' : 'text-gray-900 dark:text-gray-100'}`}>{children}</strong>
        ),
        em: ({ children }) => <em className="italic">{children}</em>,
        ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
        code: ({ children, className }) => {
          const isBlock = className?.includes('language-');
          if (isBlock) {
            return (
              <code className={`block rounded p-3 my-2 text-sm overflow-x-auto ${
                isUser ? 'bg-blue-700 text-blue-100' : 'bg-gray-800 dark:bg-gray-900 text-gray-100'
              }`}>
                {children}
              </code>
            );
          }
          return (
            <code className={`px-1.5 py-0.5 rounded text-sm font-mono ${
              isUser ? 'bg-blue-700 text-blue-100' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
            }`}>
              {children}
            </code>
          );
        },
        pre: ({ children }) => <pre className="mb-2">{children}</pre>,
        h1: ({ children }) => <h1 className={`text-lg font-bold mb-2 ${isUser ? 'text-white' : 'text-gray-900 dark:text-gray-100'}`}>{children}</h1>,
        h2: ({ children }) => <h2 className={`text-base font-bold mb-1.5 ${isUser ? 'text-white' : 'text-gray-900 dark:text-gray-100'}`}>{children}</h2>,
        h3: ({ children }) => <h3 className={`text-sm font-bold mb-1 ${isUser ? 'text-white' : 'text-gray-900 dark:text-gray-100'}`}>{children}</h3>,
        a: ({ children, href }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className={`underline ${
            isUser ? 'text-blue-200 hover:text-white' : 'text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300'
          }`}>
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className={`border-l-3 pl-3 my-2 italic ${
            isUser ? 'border-blue-300 text-blue-200' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300'
          }`}>
            {children}
          </blockquote>
        ),
        hr: () => <hr className={`my-3 ${isUser ? 'border-blue-400' : 'border-gray-300'}`} />,
        table: ({ children }) => (
          <div className="overflow-x-auto my-2">
            <table className="min-w-full text-sm border-collapse">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className={`px-2 py-1 text-left font-semibold border-b ${
            isUser ? 'border-blue-400' : 'border-gray-300'
          }`}>{children}</th>
        ),
        td: ({ children }) => (
          <td className={`px-2 py-1 border-b ${
            isUser ? 'border-blue-500/30' : 'border-gray-200'
          }`}>{children}</td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
