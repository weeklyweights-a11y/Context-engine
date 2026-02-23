import { MessageCircle } from "lucide-react";
import { useAgentChat } from "../../hooks/useAgentChat";
import AgentChatPanel from "./AgentChatPanel";

export default function AgentChatBubble() {
  const { isOpen, setIsOpen } = useAgentChat();

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg flex items-center justify-center z-40 transition-all"
        aria-label="Open agent chat"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
      <AgentChatPanel />
    </>
  );
}
