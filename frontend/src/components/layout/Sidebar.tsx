'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useProjectStore } from '@/lib/stores';
import { Project } from '@/types';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { projects, currentProject, isLoading, fetchProjects, selectProject, createProject } = useProjectStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleProjectClick = (project: Project) => {
    selectProject(project);
    router.push(`/projects/${project.id}/chat`);
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    try {
      const project = await createProject({ name: newProjectName.trim() });
      selectProject(project);
      setNewProjectName('');
      setIsCreating(false);
      router.push(`/projects/${project.id}/chat`);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const projectNavItems = currentProject
    ? [
        { name: 'Chat', href: `/projects/${currentProject.id}/chat` },
        { name: 'Tasks', href: `/projects/${currentProject.id}/tasks` },
        { name: 'Documents', href: `/projects/${currentProject.id}/documents` },
      ]
    : [];

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      <div className="p-4 border-b border-gray-700">
        <Link href="/" className="text-xl font-bold">PM Assistant</Link>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="text-sm font-medium text-gray-300 mb-2">Projects</div>
        
        {isLoading ? (
          <div className="text-sm text-gray-400">Loading...</div>
        ) : (
          <div className="space-y-1">
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => handleProjectClick(project)}
                className={`w-full text-left px-3 py-2 text-sm rounded-md ${
                  currentProject?.id === project.id
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                {project.name}
              </button>
            ))}

            {isCreating ? (
              <form onSubmit={handleCreateProject} className="mt-2">
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Project name..."
                  className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-600 rounded-md text-white"
                  autoFocus
                />
                <div className="flex gap-2 mt-2">
                  <button type="submit" className="flex-1 px-3 py-1 text-xs bg-blue-600 rounded-md">Create</button>
                  <button type="button" onClick={() => setIsCreating(false)} className="flex-1 px-3 py-1 text-xs bg-gray-700 rounded-md">Cancel</button>
                </div>
              </form>
            ) : (
              <button onClick={() => setIsCreating(true)} className="w-full px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-md">
                + New Project
              </button>
            )}
          </div>
        )}

        {currentProject && (
          <div className="mt-6 pt-4 border-t border-gray-700">
            <div className="text-xs font-medium text-gray-400 uppercase mb-2">{currentProject.name}</div>
            <nav className="space-y-1">
              {projectNavItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`block px-3 py-2 text-sm rounded-md ${
                    pathname === item.href ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-700">
        <Link href="/settings" className="block px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-md">
          Settings
        </Link>
      </div>
    </aside>
  );
}
