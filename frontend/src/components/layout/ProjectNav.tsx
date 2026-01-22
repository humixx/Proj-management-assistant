import Link from 'next/link';

interface ProjectNavProps {
  projectId: string;
  activeTab?: 'overview' | 'chat' | 'tasks' | 'documents';
}

export default function ProjectNav({ projectId, activeTab = 'overview' }: ProjectNavProps) {
  const tabs = [
    { id: 'overview', label: 'Project Overview', href: `/projects/${projectId}` },
    { id: 'chat', label: 'Chat', href: `/projects/${projectId}/chat` },
    { id: 'tasks', label: 'Tasks', href: `/projects/${projectId}/tasks` },
    { id: 'documents', label: 'Documents', href: `/projects/${projectId}/documents` },
  ];

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-4 h-12">
          {tabs.map((tab, index) => (
            <div key={tab.id} className="flex items-center">
              {index > 0 && <span className="text-gray-400 mr-4">/</span>}
              <Link
                href={tab.href}
                className={`text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'font-medium text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
