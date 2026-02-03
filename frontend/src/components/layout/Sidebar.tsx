'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useProjectStore } from '@/lib/stores';
import { Project } from '@/types';
import { validateProjectName } from '@/utils/validators';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { projects, currentProject, isLoading, fetchProjects, selectProject, createProject } = useProjectStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [nameError, setNameError] = useState('');
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileOpen(false);
  }, [pathname]);

  const handleProjectClick = (project: Project) => {
    selectProject(project);
    setIsMobileOpen(false);
    router.push(`/projects/${project.id}/chat`);
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validation = validateProjectName(newProjectName);
    if (!validation.isValid) {
      setNameError(validation.error || '');
      return;
    }
    setNameError('');
    
    try {
      const project = await createProject({ name: newProjectName.trim() });
      selectProject(project);
      setNewProjectName('');
      setIsCreating(false);
      router.push(`/projects/${project.id}/chat`);
    } catch (error) {
      console.error('Failed to create project:', error);
      setNameError('Failed to create project. Please try again.');
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
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-40 p-2 bg-gray-900 text-white rounded-lg shadow-lg hover:bg-gray-800"
        aria-label="Open menu"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Backdrop (mobile) */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-gray-900 text-white flex flex-col h-screen
          transform transition-transform duration-200 ease-in-out
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">PM Assistant</Link>
        {/* Close button (mobile only) */}
        <button
          onClick={() => setIsMobileOpen(false)}
          className="lg:hidden p-1 hover:bg-gray-800 rounded"
          aria-label="Close menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
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
                  onChange={(e) => {
                    setNewProjectName(e.target.value);
                    if (nameError) setNameError('');
                  }}
                  placeholder="Project name..."
                  className={`w-full px-3 py-2 text-sm bg-gray-800 border rounded-md text-white ${
                    nameError ? 'border-red-500' : 'border-gray-600'
                  }`}
                  autoFocus
                />
                {nameError && <p className="text-xs text-red-400 mt-1">{nameError}</p>}
                <div className="flex gap-2 mt-2">
                  <button type="submit" className="flex-1 px-3 py-1 text-xs bg-blue-600 rounded-md hover:bg-blue-700">Create</button>
                  <button 
                    type="button" 
                    onClick={() => {
                      setIsCreating(false);
                      setNameError('');
                      setNewProjectName('');
                    }} 
                    className="flex-1 px-3 py-1 text-xs bg-gray-700 rounded-md hover:bg-gray-600"
                  >
                    Cancel
                  </button>
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
    </>
  );
}
