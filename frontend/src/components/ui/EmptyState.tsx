'use client';

interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {icon && <div className="text-6xl mb-4">{icon}</div>}
      <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">{title}</h3>
      {description && <p className="text-gray-500 dark:text-gray-400 mb-4 max-w-md">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

export function NoDocumentsEmpty() {
  return (
    <EmptyState
      icon="📄"
      title="No documents yet"
      description="Upload documents to get started. Your AI assistant will analyze them and help you extract insights."
    />
  );
}

export function NoChatEmpty() {
  return (
    <EmptyState
      icon="💬"
      title="Start a conversation"
      description="Upload documents and ask me to analyze them or create tasks. I'm here to help manage your project!"
    />
  );
}

export function NoTasksEmpty() {
  return (
    <EmptyState
      icon="✓"
      title="No tasks yet"
      description="Create your first task to get started, or ask the AI assistant to help you break down your project."
    />
  );
}

export function NoProjectsEmpty() {
  return (
    <EmptyState
      icon="📁"
      title="No projects yet"
      description="Create your first project to start organizing your work and collaborating with your team."
    />
  );
}
