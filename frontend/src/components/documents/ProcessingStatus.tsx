interface ProcessingStatusProps {
  status: 'processing' | 'completed' | 'failed';
  message?: string;
}

export default function ProcessingStatus({ status, message }: ProcessingStatusProps) {
  if (status === 'processing') {
    return (
      <div className="flex items-center space-x-2 text-sm text-yellow-600">
        <svg
          className="animate-spin h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <span>{message || 'Processing document...'}</span>
      </div>
    );
  }

  if (status === 'completed') {
    return (
      <div className="flex items-center space-x-2 text-sm text-green-600">
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
        <span>{message || 'Processing completed'}</span>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="flex items-center space-x-2 text-sm text-red-600">
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
        <span>{message || 'Processing failed'}</span>
      </div>
    );
  }

  return null;
}
