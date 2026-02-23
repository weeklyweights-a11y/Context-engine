import { useState, useEffect, useRef, useCallback } from "react";
import { X, MessageCircle, Minus, History } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAgentChat } from "../../hooks/useAgentChat";
import {
  sendChatMessage,
  getConversations,
  getConversation,
  type Conversation,
} from "../../services/agentApi";

const SUGGESTED_PROMPTS = [
  "What's happening with checkout this week?",
  "What should we prioritize this quarter?",
  "Show me feedback from enterprise customers",
  "Compare pricing sentiment: enterprise vs SMB",
  "Generate specs for the top issue",
  "Which customers are at risk?",
];

export default function AgentChatPanel() {
  const { isOpen, setIsOpen, consumePendingMessage } = useAgentChat();
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (isOpen) {
      const pending = consumePendingMessage();
      if (pending) {
        setInput("");
        inputRef.current?.focus();
        setMessages((m) => [...m, { role: "user", content: pending }]);
        setLoading(true);
        setError(null);
        sendChatMessage(pending, conversationId || undefined)
          .then((res) => {
            setConversationId(res.conversation_id);
            setMessages((m) => [...m, { role: "assistant", content: res.response }]);
          })
          .catch((e: unknown) => {
            const msg = e && typeof e === "object" && "response" in e
              ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
              : "Agent temporarily unavailable";
            setError(String(msg));
            setMessages((m) => [...m, { role: "assistant", content: `Error: ${msg}` }]);
          })
          .finally(() => setLoading(false));
        setInput("");
      } else {
        inputRef.current?.focus();
      }
      getConversations()
        .then((r) => setConversations(r.data || []))
        .catch(() => setConversations([]));
    }
  }, [isOpen, consumePendingMessage]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    setError(null);
    try {
      const res = await sendChatMessage(text, conversationId || undefined);
      setConversationId(res.conversation_id);
      setMessages((m) => [...m, { role: "assistant", content: res.response }]);
      getConversations()
        .then((r) => setConversations(r.data || []))
        .catch(() => {});
    } catch (e: unknown) {
      const msg = e && typeof e === "object" && "response" in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : "Agent temporarily unavailable";
      setError(String(msg));
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    setError(null);
    setShowHistory(false);
  };

  const handleSelectConversation = async (id: string) => {
    setShowHistory(false);
    try {
      const conv = await getConversation(id);
      setConversationId(conv.id);
      const msgs = (conv.messages || []).map((m) => ({ role: m.role, content: m.content }));
      setMessages(msgs);
    } catch {
      setError("Could not load conversation");
    }
  };

  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && setIsOpen(false);
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [setIsOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" role="dialog" aria-modal aria-label="Agent chat">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={() => setIsOpen(false)}
        aria-hidden
      />
      <div
        className="relative w-full max-w-md bg-gray-900 border-l border-gray-700 shadow-xl flex flex-col z-50"
        style={{ minWidth: 400 }}
      >
        <div className="flex-shrink-0 border-b border-gray-700 p-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-indigo-400" />
            <span className="font-medium text-gray-100">Context Engine Agent</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="relative">
              <button
                type="button"
                onClick={() => setShowHistory((v) => !v)}
                className="p-1.5 rounded text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                title="History"
                aria-label="Conversation history"
              >
                <History className="w-4 h-4" />
              </button>
              {showHistory && (
                <div className="absolute right-0 top-full mt-1 w-64 max-h-64 overflow-y-auto rounded border border-gray-600 bg-gray-800 shadow-lg py-1 z-10">
                  {conversations.length === 0 ? (
                    <p className="px-3 py-2 text-gray-500 text-sm">No conversations yet</p>
                  ) : (
                    conversations.map((c) => (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => handleSelectConversation(c.id)}
                        className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700 truncate"
                      >
                        {(c.title || "Conversation").slice(0, 40)}
                        {((c.title || "").length > 40) ? "…" : ""}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={handleNewConversation}
              className="px-2 py-1 text-xs rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
            >
              New
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              aria-label="Minimize"
            >
              <Minus className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
          {messages.length === 0 && (
            <div className="space-y-3">
              <p className="text-gray-400 text-sm">Ask me anything about your feedback.</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_PROMPTS.map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => {
                      setMessages((m) => [...m, { role: "user", content: p }]);
                      setInput("");
                      setLoading(true);
                      setError(null);
                      sendChatMessage(p, conversationId || undefined)
                        .then((res) => {
                          setConversationId(res.conversation_id);
                          setMessages((m) => [...m, { role: "assistant", content: res.response }]);
                          getConversations().then((r) => setConversations(r.data || [])).catch(() => {});
                        })
                        .catch((e: unknown) => {
                          const msg = e && typeof e === "object" && "response" in e
                            ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
                            : "Agent temporarily unavailable";
                          setError(String(msg));
                          setMessages((m) => [...m, { role: "assistant", content: `Error: ${msg}` }]);
                        })
                        .finally(() => setLoading(false));
                    }}
                    className="px-3 py-1.5 text-sm rounded-full bg-gray-700 hover:bg-gray-600 text-gray-200"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-800 text-gray-200"
                }`}
              >
                {m.role === "user" ? (
                  <p className="text-sm whitespace-pre-wrap">{m.content}</p>
                ) : (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg px-3 py-2 bg-gray-800 text-gray-400 text-sm">
                Thinking…
              </div>
            </div>
          )}
          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex-shrink-0 border-t border-gray-700 p-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your feedback..."
            rows={2}
            disabled={loading}
            className="w-full px-3 py-2 rounded bg-gray-800 border border-gray-600 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 disabled:opacity-50 resize-none"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="mt-2 w-full py-2 rounded bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
