'use client';

import { useState } from 'react';
import { ProposedPlanStep } from '@/types';

const PRIORITY_STYLES: Record<string, { bg: string; text: string; dot: string }> = {
  low: { bg: 'bg-gray-50', text: 'text-gray-600', dot: 'bg-gray-400' },
  medium: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-400' },
  high: { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-400' },
  critical: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-400' },
};

interface PlanCardProps {
  goal: string;
  steps: ProposedPlanStep[];
  onApprove: (message: string) => void;
  disabled?: boolean;
}

export default function PlanCard({ goal, steps, onApprove, disabled = false }: PlanCardProps) {
  const [acted, setActed] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const isDisabled = disabled || acted;

  const handleApprove = () => {
    if (isDisabled) return;
    setActed(true);
    const stepsJson = JSON.stringify(
      steps.map(({ step_number, ...rest }) => rest),
    );
    onApprove(
      `APPROVED PLAN. Call confirm_plan now with goal: "${goal}" and steps: ${stepsJson}`,
    );
  };

  const handleReject = () => {
    if (isDisabled) return;
    setActed(true);
    onApprove('Rejected plan. Do not create these tasks.');
  };

  return (
    <div className="mt-3 rounded-xl overflow-hidden border border-indigo-200 shadow-sm">
      {/* ── Parent Goal Card ── */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3.5">
        <div className="flex items-start gap-3">
          {/* Plan icon */}
          <div className="w-9 h-9 rounded-lg bg-white/20 backdrop-blur flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-indigo-200 uppercase tracking-wider">Multi-Step Plan</span>
            </div>
            <h3 className="text-white font-semibold text-base mt-0.5 leading-snug">{goal}</h3>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-xs text-indigo-200 flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                {steps.length} steps
              </span>
              <span className="text-xs text-indigo-200 flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                Sequential
              </span>
            </div>
          </div>
          {/* Collapse toggle */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-white/70 hover:text-white p-1 rounded transition-colors flex-shrink-0"
          >
            <svg className={`w-5 h-5 transition-transform ${expanded ? '' : '-rotate-90'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* ── Subtasks (nested inside) ── */}
      {expanded && (
        <div className="bg-white">
          <div className="px-3 pt-1 pb-1">
            <div className="flex items-center gap-1.5 px-1 py-2">
              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Subtasks</span>
            </div>

            {steps.map((step, i) => {
              const priority = PRIORITY_STYLES[step.priority] || PRIORITY_STYLES.medium;
              const isLast = i === steps.length - 1;

              return (
                <div key={step.step_number} className="flex items-stretch gap-0">
                  {/* Left rail: step number + vertical connector */}
                  <div className="flex flex-col items-center w-8 flex-shrink-0">
                    <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold border-2 border-indigo-200 z-10">
                      {step.step_number}
                    </div>
                    {!isLast && (
                      <div className="w-0.5 flex-1 bg-indigo-100" />
                    )}
                  </div>

                  {/* Step card */}
                  <div className={`flex-1 min-w-0 ml-1.5 ${isLast ? 'mb-1' : 'mb-1'}`}>
                    <div className={`rounded-lg border border-gray-100 px-3 py-2.5 ${i % 2 === 0 ? 'bg-gray-50/50' : 'bg-white'} hover:border-indigo-200 transition-colors`}>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm text-gray-900 flex-1">{step.title}</span>
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${priority.bg} ${priority.text}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${priority.dot}`} />
                          {step.priority}
                        </span>
                      </div>
                      {step.description && (
                        <p className="text-xs text-gray-500 mt-1.5 leading-relaxed line-clamp-2">{step.description}</p>
                      )}
                      {(step.assignee || step.due_date) && (
                        <div className="flex items-center gap-3 mt-1.5">
                          {step.assignee && (
                            <span className="text-xs text-gray-400 flex items-center gap-1">
                              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                              </svg>
                              {step.assignee}
                            </span>
                          )}
                          {step.due_date && (
                            <span className="text-xs text-gray-400 flex items-center gap-1">
                              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              {step.due_date}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* ── Action buttons ── */}
          <div className="px-4 py-3 bg-gray-50/80 border-t border-gray-100 flex items-center gap-2">
            {acted ? (
              <span className="text-sm text-gray-500 italic flex items-center gap-1.5">
                <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Plan approved — creating tasks...
              </span>
            ) : (
              <>
                <button
                  onClick={handleApprove}
                  disabled={isDisabled}
                  className="px-4 py-1.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1.5 shadow-sm"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  Approve Plan ({steps.length} steps)
                </button>
                <button
                  onClick={handleReject}
                  disabled={isDisabled}
                  className="px-4 py-1.5 bg-white text-red-600 text-sm font-medium rounded-lg border border-red-200 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Reject
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
