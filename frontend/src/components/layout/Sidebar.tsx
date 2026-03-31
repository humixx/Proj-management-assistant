'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useProjectStore, useAuthStore } from '@/lib/stores';
import { Project } from '@/types';
import { validateProjectName } from '@/utils/validators';
import { billingApi, BillingStatus } from '@/lib/api/billing';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { projects, currentProject, isLoading, fetchProjects, selectProject, createProject } = useProjectStore();
  const { user, logout } = useAuthStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [nameError, setNameError] = useState('');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [billing, setBilling] = useState<BillingStatus | null>(null);

  useEffect(() => {
    if (user) billingApi.status().then(setBilling).catch(() => {});
  }, [user]);

  const planLabel = billing?.is_trialing
    ? `Trial · ${Math.max(0, Math.ceil((new Date(billing.trial_ends_at!).getTime() - Date.now()) / 86400000))}d left`
    : billing?.is_active
      ? 'Pro'
      : 'Free';

  const planColor = billing?.is_trialing
    ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    : billing?.is_active
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
      : 'bg-gray-700/50 text-gray-400 border-gray-600/50';

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

      <div className="p-4 border-t border-gray-700 space-y-2">
        <Link
          href="/pricing"
          className={`flex items-center justify-between px-3 py-2 text-xs font-medium rounded-md border transition-colors hover:brightness-110 ${planColor}`}
        >
          <span>{planLabel}</span>
          {!billing?.is_active || billing?.is_trialing ? (
            <span className="text-[10px] opacity-70">Upgrade →</span>
          ) : (
            <svg className="w-3.5 h-3.5 opacity-70" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          )}
        </Link>
        <Link href="/settings" className="block px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-md">
          Settings
        </Link>
        {user && (
          <div className="px-3 py-2">
            <p className="text-sm font-medium text-white truncate">{user.name}</p>
            <p className="text-xs text-gray-400 truncate">{user.email}</p>
            <button
              onClick={() => {
                logout();
                // Use window.location for full page reload to ensure cookie is cleared
                window.location.href = '/';
              }}
              className="mt-2 w-full px-3 py-1.5 text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 rounded-md transition-colors"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </aside>
    </>
  );
}
