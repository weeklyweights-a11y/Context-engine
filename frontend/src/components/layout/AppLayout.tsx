import Sidebar from "./Sidebar";
import AgentChatBubble from "../agent/AgentChatBubble";
import { AgentChatProvider } from "../../hooks/useAgentChat";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <AgentChatProvider>
      <div className="flex min-h-screen bg-gray-950 dark:bg-gray-950">
        <Sidebar />
        <main className="flex-1 overflow-auto">{children}</main>
        <AgentChatBubble />
      </div>
    </AgentChatProvider>
  );
}
