'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { integrationsApi } from '@/lib/api/integrations';
import { useProjectStore } from '@/lib/stores';
import { SlackStatus } from '@/types/integration';

export default function SlackStatusCard() {
  const { currentProject } = useProjectStore();
  const [status, setStatus] = useState<SlackStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!currentProject) {
      setIsLoading(false);
      return;
    }

    const fetchStatus = async () => {
      try {
        const data = await integrationsApi.status();
        setStatus(data);
      } catch {
        // If 404 or error, treat as not connected
        setStatus(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, [currentProject]);

  const isConnected = status?.connected === true;
  const hasCredentials = status?.has_credentials === true;

  return (
    <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${isConnected ? 'bg-green-100 dark:bg-green-900/30' : 'bg-purple-100 dark:bg-purple-900/30'}`}>
          <svg
            className={`w-5 h-5 ${isConnected ? 'text-green-600 dark:text-green-400' : 'text-purple-600 dark:text-purple-400'}`}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165V8.834a2.528 2.528 0 0 1 2.522-2.523A2.528 2.528 0 0 1 5.042 8.834v6.331zm6.804 0a2.528 2.528 0 0 1-2.521 2.523 2.528 2.528 0 0 1-2.52-2.523V8.834a2.528 2.528 0 0 1 2.52-2.523 2.528 2.528 0 0 1 2.521 2.523v6.331zm6.804 0a2.528 2.528 0 0 1-2.52 2.523 2.528 2.528 0 0 1-2.522-2.523V8.834a2.528 2.528 0 0 1 2.522-2.523 2.528 2.528 0 0 1 2.52 2.523v6.331zM5.042 8.834H2.774a.19.19 0 0 0-.189.188v6.331c0 .104.085.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188zm6.804 0H9.578a.19.19 0 0 0-.189.188v6.331c0 .104.086.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188zm6.804 0h-2.268a.19.19 0 0 0-.189.188v6.331c0 .104.085.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188z" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium">Slack</p>
          {isLoading ? (
            <p className="text-xs text-gray-400 dark:text-gray-500">Checking...</p>
          ) : isConnected ? (
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 bg-green-500 rounded-full" />
              <p className="text-xs text-green-600 dark:text-green-400 font-medium">
                Connected{status?.team_name ? ` to ${status.team_name}` : ''}
              </p>
            </div>
          ) : hasCredentials ? (
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 bg-yellow-500 rounded-full" />
              <p className="text-xs text-yellow-600 dark:text-yellow-400">Credentials saved — needs OAuth</p>
            </div>
          ) : (
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full" />
              <p className="text-xs text-gray-500 dark:text-gray-400">Not connected</p>
            </div>
          )}
        </div>
      </div>
      <Link
        href="/settings/integrations"
        className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
          isConnected
            ? 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
            : 'text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/30'
        }`}
      >
        {isConnected ? 'Manage' : 'Connect'}
      </Link>
    </div>
  );
}
