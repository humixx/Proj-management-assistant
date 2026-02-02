export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  tool_calls: Record<string, any> | null;
  created_at: string;
}

export interface ToolCallInfo {
  tool_name: string;
  arguments: Record<string, any>;
  result: any;
}

export interface PlanStep {
  step_id: number;
  action: string;
  description: string;
  status: string;
}

export interface PlanInfo {
  plan_id: string;
  goal: string;
  steps: PlanStep[];
  current_step: number;
  status: string;
}

export interface ChatRequest {
  message: string;
  include_context?: boolean;
}

export interface ChatResponse {
  message: string;
  tool_calls?: ToolCallInfo[] | null;
  plan?: PlanInfo | null;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
}

export interface LocalMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCallInfo[] | null;
  created_at: string;
  pending?: boolean;
  plan?: PlanInfo | null;
}
