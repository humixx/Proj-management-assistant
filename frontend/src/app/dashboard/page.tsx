'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useProjectStore, useAuthStore, useNotesStore } from '@/lib/stores';
import { Task, Document } from '@/types';
import apiClient from '@/lib/api/client';

interface ActivityItem {
  id: string;
  type: 'task' | 'document' | 'project';
  title: string;
  description: string;
  timestamp: string;
  projectName?: string;
}

export default function Dashboard() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { projects, fetchProjects } = useProjectStore();
  const { user, logout, isAuthenticated } = useAuthStore();
  const { notes, setNotes } = useNotesStore();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [teamMemberCount, setTeamMemberCount] = useState(0);
  const [pendingTasksCount, setPendingTasksCount] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      try {
        await fetchProjects();
        
        // Fetch tasks from all projects
        const allTasks: Task[] = [];
        const projectsData = await apiClient.get('/projects');
        
        for (const project of projectsData.data.projects || []) {
          try {
            const tasksResponse = await apiClient.get('/tasks', {
              headers: { 'X-Project-ID': project.id }
            });
            allTasks.push(...(tasksResponse.data.tasks || []));
          } catch (error) {
            console.error(`Error fetching tasks for project ${project.id}:`, error);
          }
        }
        
        // Build activity feed
        const recentActivities: ActivityItem[] = [];
        
        // Add recent tasks
        allTasks
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 10)
          .forEach(task => {
            const project = projectsData.data.projects.find((p: any) => p.id === task.project_id);
            recentActivities.push({
              id: `task-${task.id}`,
              type: 'task',
              title: task.title,
              description: `Task created with ${task.priority} priority`,
              timestamp: task.created_at,
              projectName: project?.name,
            });
          });
        
        // Add recent documents
        for (const project of projectsData.data.projects || []) {
          try {
            const docsResponse = await apiClient.get('/documents', {
              headers: { 'X-Project-ID': project.id }
            });
            (docsResponse.data.documents || [])
              .sort((a: Document, b: Document) => 
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
              )
              .slice(0, 5)
              .forEach((doc: Document) => {
                recentActivities.push({
                  id: `doc-${doc.id}`,
                  type: 'document',
                  title: doc.filename,
                  description: `Document uploaded and ${doc.processed ? 'processed' : 'processing'}`,
                  timestamp: doc.created_at,
                  projectName: project.name,
                });
              });
          } catch (error) {
            console.error(`Error fetching documents for project ${project.id}:`, error);
          }
        }
        
        // Sort all activities by timestamp and take top 10
        recentActivities.sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
        
        setActivities(recentActivities.slice(0, 10));
        
        // Get unique assignees for team member count
        const uniqueAssignees = new Set(
          allTasks.filter(t => t.assignee).map(t => t.assignee)
        );
        setTeamMemberCount(uniqueAssignees.size);
        
        // Calculate pending tasks count
        const pendingCount = allTasks.filter(
          t => t.status === 'todo' || t.status === 'in_progress'
        ).length;
        setPendingTasksCount(pendingCount);
        
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [fetchProjects, isAuthenticated]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Dashboard Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Welcome Section */}
        <div className="mb-6 sm:mb-8 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
              Welcome Back{user?.name ? `, ${user.name}` : ''}
            </h2>
            <p className="text-base sm:text-lg text-gray-700 dark:text-gray-300">
              Your AI-powered project management dashboard
            </p>
          </div>
          <div className="flex items-center gap-3">
            {mounted && (
              <button
                type="button"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors shadow-sm"
                aria-label="Toggle color mode"
              >
                {theme === 'dark' ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"
                    />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364 6.364l-1.414-1.414M8.05 8.05L6.636 6.636m0 10.728l1.414-1.414M17.95 8.05l1.414-1.414M12 7a5 5 0 100 10 5 5 0 000-10z"
                    />
                  </svg>
                )}
              </button>
            )}
            <button
              onClick={() => {
                logout();
                // Use window.location for full page reload to ensure cookie is cleared
                window.location.href = '/';
              }}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-colors shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign out
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Active Projects</p>
                <p className="text-3xl font-bold mt-2">
                  {isLoading ? '...' : projects.length}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Team Members</p>
                <p className="text-3xl font-bold mt-2">
                  {isLoading ? '...' : teamMemberCount}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Pending Tasks</p>
                <p className="text-3xl font-bold mt-2">
                  {isLoading ? '...' : pendingTasksCount}
                </p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <svg
                  className="w-6 h-6 text-yellow-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6 sm:mb-8">
          <h3 className="text-lg sm:text-xl font-bold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <Link
              href="/projects"
              className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-blue-300 transition-colors group"
            >
              <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                <svg
                  className="w-5 h-5 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="font-medium">New Project</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Create a new project</p>
              </div>
            </Link>

            <Link
              href="/teams"
              className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-green-300 transition-colors group"
            >
              <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="font-medium">Manage Teams</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">View and edit teams</p>
              </div>
            </Link>

          </div>
        </div>

        {/* Quick Notes */}
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-6 sm:mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg sm:text-xl font-bold">Quick Notes</h3>
            <span className="text-xs text-gray-400 dark:text-gray-500">Session only — cleared on logout</span>
          </div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Jot down your thoughts..."
            className="w-full min-h-[120px] px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-background text-foreground placeholder-gray-400 dark:placeholder-gray-500 resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          />
        </div>

        {/* Recent Activity Section */}
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-bold mb-4">Recent Activity</h3>
          {isLoading ? (
            <div className="text-center py-12 text-gray-700 dark:text-gray-300">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mx-auto"></div>
              </div>
            </div>
          ) : activities.length === 0 ? (
            <div className="text-center py-12 text-gray-700 dark:text-gray-300">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <p className="mt-4 text-base text-gray-600 dark:text-gray-300 font-medium">No recent activity</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Get started by creating a project or adding team members</p>
            </div>
          ) : (
            <div className="space-y-4">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700"
                >
                  <div className={`p-2 rounded-lg mr-4 ${
                    activity.type === 'task' ? 'bg-yellow-100' :
                    activity.type === 'document' ? 'bg-blue-100' :
                    'bg-green-100'
                  }`}>
                    {activity.type === 'task' && (
                      <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    )}
                    {activity.type === 'document' && (
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    )}
                    {activity.type === 'project' && (
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{activity.title}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{activity.description}</p>
                    {activity.projectName && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Project: <span className="font-medium">{activity.projectName}</span>
                      </p>
                    )}
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(activity.timestamp).toLocaleDateString([], { 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
