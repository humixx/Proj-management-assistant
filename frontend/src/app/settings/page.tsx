import Link from 'next/link';

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Project Management Assistant
              </h1>
            </Link>
            <div className="flex items-center space-x-4">
              <Link
                href="/projects"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Projects
              </Link>
              <Link
                href="/teams"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Teams
              </Link>
              <Link
                href="/settings"
                className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-md"
              >
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Settings</h2>
          <p className="text-gray-600">Manage your account and preferences</p>
        </div>

        {/* Settings Sections */}
        <div className="space-y-6">
          {/* General Settings */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">General</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="your.email@example.com"
                />
              </div>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
                Save Changes
              </button>
            </div>
          </div>

          {/* RAG Settings */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">RAG Configuration</h3>
              <Link
                href="/settings/rag"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Configure →
              </Link>
            </div>
            <p className="text-sm text-gray-600">
              Configure document processing and vector search settings
            </p>
          </div>

          {/* Integrations */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Integrations</h3>
              <Link
                href="/settings/integrations"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Manage →
              </Link>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg
                      className="w-5 h-5 text-purple-600"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165V8.834a2.528 2.528 0 0 1 2.522-2.523A2.528 2.528 0 0 1 5.042 8.834v6.331zm6.804 0a2.528 2.528 0 0 1-2.521 2.523 2.528 2.528 0 0 1-2.52-2.523V8.834a2.528 2.528 0 0 1 2.52-2.523 2.528 2.528 0 0 1 2.521 2.523v6.331zm6.804 0a2.528 2.528 0 0 1-2.52 2.523 2.528 2.528 0 0 1-2.522-2.523V8.834a2.528 2.528 0 0 1 2.522-2.523 2.528 2.528 0 0 1 2.52 2.523v6.331zM5.042 8.834H2.774a.19.19 0 0 0-.189.188v6.331c0 .104.085.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188zm6.804 0H9.578a.19.19 0 0 0-.189.188v6.331c0 .104.086.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188zm6.804 0h-2.268a.19.19 0 0 0-.189.188v6.331c0 .104.085.188.189.188h2.268a.19.19 0 0 0 .189-.188V9.022a.19.19 0 0 0-.189-.188z"/>
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Slack</p>
                    <p className="text-xs text-gray-500">Not connected</p>
                  </div>
                </div>
                <button className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 font-medium">
                  Connect
                </button>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferences</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Email Notifications</p>
                  <p className="text-xs text-gray-500">Receive email updates about your projects</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Dark Mode</p>
                  <p className="text-xs text-gray-500">Switch to dark theme</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
