'use client';

import { useChatStore, AgentStatus } from '@/lib/stores/chatStore';

const STAGE_CONFIG: Record<string, { icon: string; color: string }> = {
  create_task: { icon: '✏️', color: 'bg-green-500' },
  bulk_create_tasks: { icon: '📋', color: 'bg-green-500' },
  list_tasks: { icon: '📄', color: 'bg-blue-500' },
  search_documents: { icon: '🔍', color: 'bg-purple-500' },
  propose_tasks: { icon: '📝', color: 'bg-yellow-500' },
  confirm_proposed_tasks: { icon: '✅', color: 'bg-green-500' },
  update_task: { icon: '✏️', color: 'bg-blue-500' },
  delete_task: { icon: '🗑️', color: 'bg-red-500' },
  propose_plan: { icon: '🗺️', color: 'bg-indigo-500' },
  confirm_plan: { icon: '🏗️', color: 'bg-indigo-500' },
  list_slack_channels: { icon: '🔈', color: 'bg-teal-500' },
  send_slack_message: { icon: '📨', color: 'bg-teal-600' },
};

const FALLBACK_STAGES: Record<AgentStatus['stage'], { icon: string; color: string }> = {
  idle: { icon: '⏸️', color: 'bg-gray-400' },
  analyzing: { icon: '🔍', color: 'bg-blue-500' },
  calling_llm: { icon: '🧠', color: 'bg-indigo-500' },
  tool_running: { icon: '⚙️', color: 'bg-amber-500' },
  tool_done: { icon: '✅', color: 'bg-green-500' },
  composing: { icon: '✍️', color: 'bg-teal-500' },
  responding: { icon: '💬', color: 'bg-blue-500' },
};

interface ThinkingIndicatorProps {
  /** If provided, uses this status instead of the store */
  status?: AgentStatus;
  compact?: boolean;
}

export default function ThinkingIndicator({ status: statusProp, compact = false }: ThinkingIndicatorProps) {
  const storeStatus = useChatStore((s) => s.agentStatus);
  const status = statusProp || storeStatus;

  // Hide when idle or when text is actively streaming into the message bubble
  if (status.stage === 'idle' || status.stage === 'responding') return null;

  const toolConfig = status.toolName ? STAGE_CONFIG[status.toolName] : null;
  const config = toolConfig || FALLBACK_STAGES[status.stage];

  // Extract a human-friendly detail from tool args
  let detail: string | null = null;
  if (status.stage === 'tool_running' && status.toolArgs) {
    if (status.toolName === 'create_task' && status.toolArgs.title) {
      detail = `"${status.toolArgs.title}"`;
    } else if (status.toolName === 'bulk_create_tasks' && status.toolArgs.tasks) {
      detail = `${status.toolArgs.tasks.length} tasks`;
    } else if (status.toolName === 'propose_tasks' && status.toolArgs.tasks) {
      detail = `${status.toolArgs.tasks.length} task(s)`;
    } else if (status.toolName === 'confirm_proposed_tasks' && status.toolArgs.tasks) {
      detail = `${status.toolArgs.tasks.length} task(s)`;
    } else if (status.toolName === 'update_task' && status.toolArgs.task_id) {
      const changes = ['status', 'priority', 'title', 'assignee'].filter((k) => status.toolArgs?.[k]).join(', ');
      detail = changes || 'updating';
    } else if (status.toolName === 'delete_task') {
      detail = 'removing task';
    } else if (status.toolName === 'propose_plan' && status.toolArgs.goal) {
      detail = `"${status.toolArgs.goal}"`;
    } else if (status.toolName === 'list_slack_channels') {
      detail = 'listing channels';
    } else if (status.toolName === 'send_slack_message' && status.toolArgs?.channel) {
      detail = `#${status.toolArgs.channel}`;
    } else if (status.toolName === 'confirm_plan' && status.toolArgs.steps) {
      detail = `${status.toolArgs.steps.length} step(s)`;
    } else if (status.toolName === 'search_documents' && status.toolArgs.query) {
      detail = `"${status.toolArgs.query}"`;
    } else if (status.toolName === 'list_tasks') {
      const filters = [status.toolArgs.status, status.toolArgs.priority].filter(Boolean).join(', ');
      detail = filters || 'all tasks';
    }
  }
  if (status.stage === 'tool_done' && status.toolResult) {
    if (status.toolName === 'propose_plan' && status.toolResult.steps?.length) {
      detail = `${status.toolResult.steps.length} steps proposed`;
    } else if (status.toolName === 'confirm_plan' && status.toolResult.steps?.length) {
      detail = `${status.toolResult.steps.length} steps created`;
    } else if (status.toolName === 'propose_tasks' && status.toolResult.tasks?.length) {
      detail = `${status.toolResult.tasks.length} proposed`;
    } else if (status.toolName === 'update_task' && status.toolResult.task?.title) {
      detail = `"${status.toolResult.task.title}"`;
    } else if (status.toolName === 'delete_task' && status.toolResult.message) {
      detail = 'removed';
    } else if (status.toolResult.count) {
      detail = `${status.toolResult.count} created`;
    } else if (status.toolResult.task?.title) {
      detail = `"${status.toolResult.task.title}"`;
    } else if (status.toolResult.tasks?.length) {
      detail = `${status.toolResult.tasks.length} found`;
    }
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        <span className="animate-pulse">
          {config.icon} {status.label}
          {detail && <span className="text-gray-400 dark:text-gray-500 ml-1">— {detail}</span>}
        </span>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-100 dark:border-blue-800 rounded-xl px-4 py-3 max-w-sm">
        <div className="flex items-center gap-3">
          <div className="relative flex-shrink-0">
            <div className={`w-8 h-8 rounded-full ${config.color} flex items-center justify-center`}>
              <span className="text-sm">{config.icon}</span>
            </div>
            {status.stage !== 'tool_done' && (
              <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
              {status.label}
            </p>
            {detail && (
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                {detail}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
