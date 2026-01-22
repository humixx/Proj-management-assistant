import Link from 'next/link';

export default function Header() {
  return (
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
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              Settings
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
