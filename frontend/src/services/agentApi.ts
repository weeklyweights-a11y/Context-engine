import { api } from "./api";

const PREFIX = "/agent";

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tools_used: unknown[];
  citations: Array<{ feedback_id?: string; text?: string; customer_id?: string }>;
}

export interface Conversation {
  id: string;
  org_id: string;
  user_id: string;
  kibana_conversation_id?: string;
  title: string;
  messages: Array<{ role: string; content: string; timestamp?: string }>;
  created_at: string;
  updated_at: string;
}

/** Send a chat message to the agent. */
export async function sendChatMessage(
  message: string,
  conversationId?: string,
  context?: Record<string, unknown>
): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>(`${PREFIX}/chat`, {
    message,
    conversation_id: conversationId ?? null,
    context: context ?? null,
  });
  return data;
}

/** List conversations for the current user. */
export async function getConversations(): Promise<{ data: Conversation[] }> {
  const { data } = await api.get<{ data: Conversation[] }>(`${PREFIX}/conversations`);
  return data;
}

/** Get a single conversation by ID. */
export async function getConversation(id: string): Promise<Conversation> {
  const { data } = await api.get<Conversation>(`${PREFIX}/conversations/${id}`);
  return data;
}
