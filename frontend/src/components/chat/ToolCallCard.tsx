interface ToolCallCardProps {
  toolName: string;
  arguments: Record<string, any>;
  result?: any;
  status?: 'pending' | 'success' | 'error';
}

export default function ToolCallCard({
  toolName,
  arguments: args,
  result,
  status = 'pending',
}: ToolCallCardProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 my-2">
      <div className="flex items-center space-x-2 mb-2">
        <svg
          className="w-4 h-4 text-yellow-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <span className="text-sm font-medium text-yellow-800">
          Tool: {toolName}
        </span>
        {status === 'pending' && (
          <span className="text-xs text-yellow-600">Executing...</span>
        )}
        {status === 'success' && (
          <span className="text-xs text-green-600">✓ Completed</span>
        )}
        {status === 'error' && (
          <span className="text-xs text-red-600">✗ Failed</span>
        )}
      </div>
      <div className="text-xs text-yellow-700 space-y-1">
        <div>
          <span className="font-medium">Arguments:</span>
          <pre className="mt-1 text-xs bg-yellow-100 p-2 rounded overflow-x-auto">
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>
        {result && (
          <div>
            <span className="font-medium">Result:</span>
            <pre className="mt-1 text-xs bg-yellow-100 p-2 rounded overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
