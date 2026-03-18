'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useAuthStore } from '@/lib/stores';

export default function LandingPage() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Redirect to dashboard if already authenticated
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">PM Assistant</h1>
            </div>
            <div className="flex items-center gap-4">

              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium bg-black dark:bg-white text-white dark:text-black rounded-lg hover:bg-gray-800 dark:hover:bg-gray-200 transition-all duration-300 transform hover:scale-105"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 overflow-hidden min-h-[90vh] flex flex-col justify-center">
        {/* Subtle Minimalist Spotlight Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gray-300/30 dark:bg-white/5 rounded-full mix-blend-screen filter blur-[120px] opacity-70 animate-pulse" style={{ animationDuration: '6s' }}></div>
        
        {/* Prominent Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808033_1px,transparent_1px),linear-gradient(to_bottom,#80808033_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_70%_50%_at_50%_0%,#000_80%,transparent_100%)] pointer-events-none"></div>

        {/* 3D Wireframe Holosphere */}
        <div className="absolute top-1/2 left-1/2 w-[1100px] h-[1100px] -translate-x-1/2 -translate-y-1/2 [perspective:1400px] pointer-events-none z-0">
          <div className="w-full h-full animate-[spin_30s_linear_infinite] [transform-style:preserve-3d]">
            <div className="absolute inset-0 rounded-full border-[4px] border-blue-500/50 dark:border-blue-400/50 [transform:rotateX(75deg)_rotateY(0deg)] drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]"></div>
            <div className="absolute inset-0 rounded-full border-[4px] border-purple-500/50 dark:border-purple-400/50 [transform:rotateX(75deg)_rotateY(45deg)] drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]"></div>
            <div className="absolute inset-0 rounded-full border-[4px] border-cyan-500/50 dark:border-cyan-400/50 [transform:rotateX(75deg)_rotateY(90deg)] drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]"></div>
            <div className="absolute inset-0 rounded-full border-[4px] border-emerald-500/50 dark:border-emerald-400/50 [transform:rotateX(75deg)_rotateY(135deg)] drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]"></div>
          </div>
        </div>

        <div className="text-center py-20 sm:py-28 relative z-10 flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 mb-8 rounded-full border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 backdrop-blur-md text-xs font-semibold tracking-wider uppercase text-gray-600 dark:text-gray-400 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-gray-500 opacity-75 duration-1000"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-gray-400"></span>
            </span>
            Introducing PM Intelligence
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter mb-6 opacity-0 animate-[fadeIn_0.5s_ease-out_0.2s_forwards] text-black dark:text-white max-w-4xl mx-auto leading-tight">
            Manage projects at the speed of thought.
          </h1>
          <p className="text-xl sm:text-2xl text-gray-500 dark:text-gray-400 mb-10 max-w-2xl mx-auto opacity-0 animate-[fadeIn_0.5s_ease-out_0.4s_forwards] font-light">
            An AI-first workspace that deeply understands your team's workflow, documents, and tasks. No clutter, just focus.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center opacity-0 animate-[fadeIn_0.5s_ease-out_0.6s_forwards] w-full max-w-md">
            <Link
              href="/register"
              className="w-full sm:w-auto px-8 py-3.5 bg-black dark:bg-white text-white dark:text-black text-lg font-medium rounded-full hover:bg-gray-800 dark:hover:bg-gray-200 transition-all duration-300 transform hover:scale-105 shadow-[0_0_20px_rgba(0,0,0,0.1)] dark:shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              Start Building
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent text-gray-600 dark:text-gray-300 text-lg font-medium hover:text-black dark:hover:text-white transition-all duration-300 flex items-center justify-center gap-2 group"
            >
              Sign In
              <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" /></svg>
            </Link>
          </div>
        </div>
        {/* Features Section */}
        <div className="pt-8 pb-16 sm:pt-12 sm:pb-20 relative z-10 w-full">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-10">
            Everything you need to manage projects
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-transparent rounded-2xl p-8 border border-gray-200 dark:border-gray-800 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-[0_0_30px_-5px_rgba(59,130,246,0.3)] hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all duration-500 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-100/50 to-transparent dark:from-blue-500/10 dark:to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="w-10 h-10 rounded-full flex items-center justify-center mb-6 text-black dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 border border-gray-200 dark:border-gray-800 group-hover:border-blue-200 dark:group-hover:border-blue-800 bg-white dark:bg-black group-hover:bg-blue-50 dark:group-hover:bg-blue-900/40 relative z-10 group-hover:scale-110 transition-all duration-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium tracking-tight mb-3 text-black dark:text-white relative z-10">AI Assistant</h3>
              <p className="text-gray-500 dark:text-gray-400 font-light leading-relaxed relative z-10">
                Chat with an intelligent AI that helps you create tasks, analyze documents, and manage your projects effortlessly.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-transparent rounded-2xl p-8 border border-gray-200 dark:border-gray-800 hover:border-emerald-400 dark:hover:border-emerald-500 hover:shadow-[0_0_30px_-5px_rgba(16,185,129,0.3)] hover:bg-emerald-50/50 dark:hover:bg-emerald-900/10 transition-all duration-500 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-100/50 to-transparent dark:from-emerald-500/10 dark:to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="w-10 h-10 rounded-full flex items-center justify-center mb-6 text-black dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 border border-gray-200 dark:border-gray-800 group-hover:border-emerald-200 dark:group-hover:border-emerald-800 bg-white dark:bg-black group-hover:bg-emerald-50 dark:group-hover:bg-emerald-900/40 relative z-10 group-hover:scale-110 transition-all duration-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-medium tracking-tight mb-3 text-black dark:text-white relative z-10">Smart Task Management</h3>
              <p className="text-gray-500 dark:text-gray-400 font-light leading-relaxed relative z-10">
                Organize tasks with Kanban boards, priorities, and AI-powered suggestions to keep your team productive.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-transparent rounded-2xl p-8 border border-gray-200 dark:border-gray-800 hover:border-purple-400 dark:hover:border-purple-500 hover:shadow-[0_0_30px_-5px_rgba(168,85,247,0.3)] hover:bg-purple-50/50 dark:hover:bg-purple-900/10 transition-all duration-500 group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-100/50 to-transparent dark:from-purple-500/10 dark:to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="w-10 h-10 rounded-full flex items-center justify-center mb-6 text-black dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 border border-gray-200 dark:border-gray-800 group-hover:border-purple-200 dark:group-hover:border-purple-800 bg-white dark:bg-black group-hover:bg-purple-50 dark:group-hover:bg-purple-900/40 relative z-10 group-hover:scale-110 transition-all duration-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium tracking-tight mb-3 text-black dark:text-white relative z-10">Document Intelligence</h3>
              <p className="text-gray-500 dark:text-gray-400 font-light leading-relaxed relative z-10">
                Upload documents and let AI analyze them, extract insights, and answer questions about your project files.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="pt-8 pb-32 sm:pt-12 sm:pb-32 text-center w-full">
          <div className="bg-black dark:bg-white rounded-[2.5rem] p-16 text-white dark:text-black shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-800 to-transparent dark:from-gray-200 opacity-50 pointer-events-none"></div>
            <div className="relative z-10">
              <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-6">
                Ready to transform your workflow?
              </h2>
              <p className="text-xl mb-10 text-gray-400 dark:text-gray-600 font-light max-w-2xl mx-auto">
                Join teams already using AI to streamline their project management.
              </p>
              <Link
                href="/register"
                className="inline-block px-10 py-4 bg-white dark:bg-black text-black dark:text-white text-lg font-medium rounded-full hover:scale-105 transition-all duration-300"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p>© 2026 PM Assistant. Built with AI-powered intelligence.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
