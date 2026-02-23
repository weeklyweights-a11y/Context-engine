import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from "react";

interface AgentChatContextValue {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  openWithMessage: (message?: string) => void;
  consumePendingMessage: () => string | undefined;
}

const AgentChatContext = createContext<AgentChatContextValue | null>(null);

export function AgentChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const pendingRef = useRef<string | undefined>();

  const openWithMessage = useCallback((message?: string) => {
    if (message) pendingRef.current = message;
    setIsOpen(true);
  }, []);

  const consumePendingMessage = useCallback(() => {
    const m = pendingRef.current;
    pendingRef.current = undefined;
    return m;
  }, []);

  const value: AgentChatContextValue = {
    isOpen,
    setIsOpen,
    openWithMessage,
    consumePendingMessage,
  };

  return (
    <AgentChatContext.Provider value={value}>
      {children}
    </AgentChatContext.Provider>
  );
}

export function useAgentChat() {
  const ctx = useContext(AgentChatContext);
  if (!ctx) {
    throw new Error("useAgentChat must be used within AgentChatProvider");
  }
  return ctx;
}
