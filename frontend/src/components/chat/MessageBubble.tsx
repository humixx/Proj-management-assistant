'use client';

import { LocalMessage, ProposedTask } from '@/types';
import { useChatStore, useTaskStore } from '@/lib/stores';
import TaskProposalCard from './TaskProposalCard';
import PlanCard from './PlanCard';
import MarkdownContent from './MarkdownContent';

const TASK_MUTATING_TOOLS = ['create_task', 'bulk_create_tasks', 'confirm_proposed_tasks', 'update_task', 'delete_task', 'confirm_plan'];

interface MessageBubbleProps {
  message: LocalMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const { sendMessageStreaming, isSending } = useChatStore();
  const { fetchTasks } = useTaskStore();

  // Normalize tool_calls: from DB it can be {calls: [...]} object, from streaming it's an array
  const toolCallsArray = Array.isArray(message.tool_calls)
    ? message.tool_calls
    : (message.tool_calls as any)?.calls || [];

  // Check if any tool call is a proposal
  const proposalCall = toolCallsArray.find(
    (tc: any) => tc.tool_name === 'propose_tasks' && tc.result?.type === 'proposal'
  );
  const proposedTasks: ProposedTask[] | null = proposalCall?.result?.tasks || null;

  // Check if any tool call is a plan proposal
  const planProposalCall = toolCallsArray.find(
    (tc: any) => tc.tool_name === 'propose_plan' && tc.result?.type === 'plan_proposal'
  );
  const planProposal = planProposalCall?.result || null;

  const handleProposalAction = async (approvalMessage: string) => {
    const response = await sendMessageStreaming(approvalMessage);
    // Refresh task panel if the agent created/updated/deleted tasks
    if (response?.tool_calls?.some((tc) => TASK_MUTATING_TOOLS.includes(tc.tool_name))) {
      await fetchTasks();
    }
  };

  // Clean up approval messages — hide the JSON payload from the user
  let displayContent = message.content;
  if (isUser) {
    if (message.content.startsWith('APPROVED PLAN.')) {
      displayContent = 'Approved plan.';
    } else if (message.content.startsWith('APPROVED.')) {
      displayContent = message.content.includes('only the selected')
        ? 'Approved selected tasks.'
        : 'Approved all tasks.';
    }
  }

  // Non-proposal tool calls for display (filter out both task proposals and plan proposals)
  const otherToolCalls = toolCallsArray.filter(
    (tc: any) =>
      !(tc.tool_name === 'propose_tasks' && tc.result?.type === 'proposal') &&
      !(tc.tool_name === 'propose_plan' && tc.result?.type === 'plan_proposal'),
  );

  // If the assistant message has no text content but has tool results,
  // build a summary from the tool results so the user sees something meaningful.
  const hasContent = displayContent && displayContent.trim().length > 0;
  const showToolSummary = !isUser && !hasContent && otherToolCalls.length > 0;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-3 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
        {hasContent && (
          isUser ? (
            <div className="whitespace-pre-wrap text-base leading-relaxed">{displayContent}</div>
          ) : (
            <div className="text-base leading-relaxed prose-sm">
              <MarkdownContent content={displayContent} />
            </div>
          )
        )}

        {/* Render proposal card if this message contains a propose_tasks tool call */}
        {proposedTasks && proposedTasks.length > 0 && (
          <TaskProposalCard
            tasks={proposedTasks}
            onApprove={handleProposalAction}
            disabled={isSending}
          />
        )}

        {/* Render plan card if this message contains a propose_plan tool call */}
        {planProposal && planProposal.steps?.length > 0 && (
          <PlanCard
            goal={planProposal.goal}
            steps={planProposal.steps}
            onApprove={handleProposalAction}
            disabled={isSending}
          />
        )}

        {/* Render non-proposal tool calls */}
        {otherToolCalls.length > 0 && (
          <div className={hasContent ? 'mt-2 space-y-1' : 'space-y-1'}>
            {otherToolCalls.map((tc: any, i: number) => (
              <div key={i} className="bg-white rounded p-2 text-xs text-gray-700 border">
                <span className="font-semibold">{tc.tool_name}</span>
                {tc.result?.message && <span className="ml-2 text-gray-600">{tc.result.message}</span>}
              </div>
            ))}
          </div>
        )}

        <div className={`text-xs mt-2 ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
