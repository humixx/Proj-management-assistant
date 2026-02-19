'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import integrationsApi from '@/lib/api/integrations';
import { SlackChannel, SlackStatus } from '@/types';
import { useUIStore } from '@/lib/stores/uiStore';
import { useProjectStore } from '@/lib/stores';

export default function IntegrationsPage() {
  const { currentProject } = useProjectStore();
  const backHref = currentProject ? `/projects/${currentProject.id}/chat` : '/';
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [status, setStatus] = useState<SlackStatus | null>(null);
  const [channels, setChannels] = useState<SlackChannel[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const addToast = useUIStore((s) => s.addToast);

  const fetchStatus = async () => {
    try {
      const s = await integrationsApi.status();
      setStatus(s as SlackStatus);
    } catch {
      setStatus(null);
    }
  };

  useEffect(() => {
    fetchStatus();

    // Handle OAuth callback — Slack redirects back with ?code=
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      (async () => {
        setLoading(true);
        try {
          const redirectUri = `${window.location.origin}${window.location.pathname}`;
          await integrationsApi.callback(code, redirectUri);
          // Clean URL
          window.history.replaceState({}, document.title, window.location.pathname);
          await fetchStatus();
          addToast('success', 'Slack connected successfully!');
        } catch {
          addToast('error', 'Failed to complete Slack connection. Please try again.');
        } finally {
          setLoading(false);
        }
      })();
    }
  }, []);

  const handleSaveCredentials = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientId.trim() || !clientSecret.trim()) {
      addToast('error', 'Please enter both Client ID and Client Secret.');
      return;
    }
    setLoading(true);
    try {
      const res = await integrationsApi.setup(clientId.trim(), clientSecret.trim());
      if (res?.oauth_url) {
        const redirectUri = `${window.location.origin}${window.location.pathname}`;
        const joiner = res.oauth_url.includes('?') ? '&' : '?';
        const full = `${res.oauth_url}${joiner}redirect_uri=${encodeURIComponent(redirectUri)}`;
        window.open(full, '_blank');
        addToast('success', 'Credentials saved! Complete the OAuth flow in the Slack window.');
      } else {
        addToast('success', 'Credentials saved.');
      }
      await fetchStatus();
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to save credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleListChannels = async () => {
    setLoading(true);
    try {
      const res = await integrationsApi.channels();
      setChannels(res.channels || []);
      if (res.channels?.length === 0) {
        addToast('info', 'No channels found. Make sure the bot is added to channels.');
      }
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to fetch channels.');
    } finally {
      setLoading(false);
    }
  };

  const handleSetDefault = async (ch: SlackChannel) => {
    setLoading(true);
    try {
      await integrationsApi.setDefaultChannel(ch.id, ch.name);
      addToast('success', `Default channel set to #${ch.name}`);
      await fetchStatus();
    } catch {
      addToast('error', 'Failed to set default channel.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    setLoading(true);
    try {
      await integrationsApi.disconnect();
      addToast('success', 'Slack disconnected.');
      setStatus(null);
      setChannels([]);
      setClientId('');
      setClientSecret('');
    } catch {
      addToast('error', 'Failed to disconnect.');
    } finally {
      setLoading(false);
      setShowDisconnectConfirm(false);
    }
  };

  const isConnected = status?.connected ?? false;
  const hasCredentials = status?.has_credentials ?? false;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href={backHref} className="flex items-center">
              <h1 className="text-xl font-bold">Project Management Assistant</h1>
            </Link>
            <div className="flex items-center space-x-4">
              <Link
                href={backHref}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
              >
                ← Back to {currentProject ? currentProject.name : 'Dashboard'}
              </Link>
              <Link
                href="/settings"
                className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded-md"
              >
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
            <Link href="/settings" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Settings</Link>
            <span>/</span>
            <span className="text-gray-900 dark:text-gray-100">Integrations</span>
          </div>
          <h2 className="text-3xl font-bold mb-2">Slack Integration</h2>
          <p className="text-gray-600 dark:text-gray-300">Connect a Slack app to this project to send messages via the AI agent.</p>
        </div>

        <div className="space-y-6">
          {/* Status Card */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* Slack Logo */}
                <div className={`p-3 rounded-lg ${isConnected ? 'bg-green-50 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-800'}`}>
                  <svg className={`w-8 h-8 ${isConnected ? 'text-green-600' : 'text-gray-400'}`} viewBox="0 0 24 24" fill="currentColor">
                    <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.163 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.163 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.163 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zm0-1.27a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.315A2.528 2.528 0 0 1 24 15.163a2.528 2.528 0 0 1-2.522 2.523h-6.315z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Slack</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`inline-flex items-center gap-1.5 text-sm ${
                        isConnected ? 'text-green-600' : hasCredentials ? 'text-yellow-600' : 'text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full ${
                          isConnected ? 'bg-green-500' : hasCredentials ? 'bg-yellow-500' : 'bg-gray-400'
                        }`}
                      />
                      {isConnected ? 'Connected' : hasCredentials ? 'Credentials saved — complete OAuth' : 'Not configured'}
                    </span>
                  </div>
                </div>
              </div>
              {isConnected && (
                <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                  {status?.team_name && <p className="font-medium text-gray-700 dark:text-gray-200">{status.team_name}</p>}
                  {status?.channel_name && (
                    <p>
                      Default: <span className="text-blue-600 dark:text-blue-400">#{status.channel_name}</span>
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Credentials / Setup */}
          {!isConnected && (
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold mb-1">Setup</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Enter your Slack App&apos;s Client ID and Client Secret. Each project can have its own Slack app.
              </p>
              <form onSubmit={handleSaveCredentials} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Client ID</label>
                  <input
                    type="text"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                    placeholder="e.g. 1234567890.1234567890"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Client Secret</label>
                  <input
                    type="password"
                    value={clientSecret}
                    onChange={(e) => setClientSecret(e.target.value)}
                    placeholder="Paste your client secret"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !clientId.trim() || !clientSecret.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Saving...' : 'Save & Connect to Slack'}
                </button>
              </form>
            </div>
          )}

          {/* Connected Actions */}
          {isConnected && (
            <>
              {/* Channels */}
              <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">Channels</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Select a default channel for agent messages.</p>
                  </div>
                  <button
                    onClick={handleListChannels}
                    disabled={loading}
                    className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium text-sm disabled:opacity-50"
                  >
                    {loading ? 'Loading...' : 'Refresh Channels'}
                  </button>
                </div>

                {channels.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <svg className="mx-auto h-10 w-10 text-gray-300 dark:text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
                    </svg>
                    <p className="text-sm">Click &quot;Refresh Channels&quot; to load available channels.</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {channels.map((ch) => (
                      <div
                        key={ch.id}
                        className={`flex items-center justify-between p-3 border rounded-lg transition-colors ${
                          status?.channel_id === ch.id
                            ? 'border-blue-300 bg-blue-50 dark:bg-blue-900/30'
                            : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400 text-sm">#</span>
                          <span className="text-sm font-medium">{ch.name}</span>
                          {status?.channel_id === ch.id && (
                            <span className="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full font-medium">
                              Default
                            </span>
                          )}
                        </div>
                        {status?.channel_id !== ch.id && (
                          <button
                            onClick={() => handleSetDefault(ch)}
                            disabled={loading}
                            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium disabled:opacity-50"
                          >
                            Set as Default
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Danger Zone */}
              <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-red-200 dark:border-red-800 p-6">
                <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-1">Danger Zone</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Disconnecting will remove all Slack credentials and tokens for this project.
                </p>
                {!showDisconnectConfirm ? (
                  <button
                    onClick={() => setShowDisconnectConfirm(true)}
                    className="px-4 py-2 bg-white dark:bg-gray-900 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors font-medium text-sm"
                  >
                    Disconnect Slack
                  </button>
                ) : (
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">Are you sure?</span>
                    <button
                      onClick={handleDisconnect}
                      disabled={loading}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-sm disabled:opacity-50"
                    >
                      {loading ? 'Disconnecting...' : 'Yes, Disconnect'}
                    </button>
                    <button
                      onClick={() => setShowDisconnectConfirm(false)}
                      className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
