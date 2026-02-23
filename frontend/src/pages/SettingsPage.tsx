import { useState, useEffect } from "react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import ThemeToggle from "../components/layout/ThemeToggle";
import ProductWizard from "../components/wizard/ProductWizard";
import FeedbackUpload from "../components/upload/FeedbackUpload";
import CustomerUpload from "../components/upload/CustomerUpload";
import UploadHistoryTable from "../components/upload/UploadHistoryTable";

type Tab = "product" | "upload" | "connectors" | "account" | "elasticsearch";

interface HealthData {
  status: string;
  elasticsearch?: { status: string; cluster_name?: string; version?: string; error?: string };
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("product");
  const [health, setHealth] = useState<HealthData | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (activeTab === "elasticsearch") {
      setHealthLoading(true);
      api
        .get<HealthData>("/health")
        .then((res) => setHealth(res.data))
        .catch(() => setHealth({ status: "error" }))
        .finally(() => setHealthLoading(false));
    }
  }, [activeTab]);

  const tabs: { id: Tab; label: string }[] = [
    { id: "product", label: "Product Wizard" },
    { id: "upload", label: "Data Upload" },
    { id: "connectors", label: "Connectors" },
    { id: "account", label: "Account" },
    { id: "elasticsearch", label: "Elasticsearch" },
  ];

  return (
    <div className="p-8">
      <h2 className="text-xl font-semibold text-gray-100 mb-6">Settings</h2>
      <div className="flex gap-4">
        <div className="w-48 flex flex-col gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-left ${
                activeTab === tab.id
                  ? "bg-blue-500 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="flex-1 bg-gray-800 rounded-lg p-6 min-h-[300px]">
          {activeTab === "product" && (
            <ProductWizard mode="settings" />
          )}
          {activeTab === "upload" && (
            <div className="space-y-8">
              <section>
                <h3 className="font-medium text-gray-100 mb-4">Upload Feedback</h3>
                <FeedbackUpload />
              </section>
              <section>
                <h3 className="font-medium text-gray-100 mb-4">Upload Customers</h3>
                <CustomerUpload />
              </section>
              <section>
                <h3 className="font-medium text-gray-100 mb-4">Upload History</h3>
                <UploadHistoryTable />
              </section>
            </div>
          )}
          {activeTab === "connectors" && (
            <p className="text-gray-400">Coming in Phase 8</p>
          )}
          {activeTab === "account" && (
            <div className="space-y-4">
              {user && (
                <>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Email</label>
                    <p className="text-gray-100">{user.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Theme</label>
                    <ThemeToggle />
                  </div>
                </>
              )}
            </div>
          )}
          {activeTab === "elasticsearch" && (
            <div className="space-y-4">
              <h3 className="font-medium text-gray-100">Connection status</h3>
              {healthLoading ? (
                <p className="text-gray-400">Checking...</p>
              ) : health ? (
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="text-gray-400">Status: </span>
                    <span
                      className={
                        health.status === "healthy"
                          ? "text-green-400"
                          : "text-yellow-400"
                      }
                    >
                      {health.status}
                    </span>
                  </p>
                  {health.elasticsearch && (
                    <>
                      <p>
                        <span className="text-gray-400">ES: </span>
                        {health.elasticsearch.status}
                      </p>
                      {health.elasticsearch.cluster_name && (
                        <p>
                          <span className="text-gray-400">Cluster: </span>
                          {health.elasticsearch.cluster_name}
                        </p>
                      )}
                      {health.elasticsearch.version && (
                        <p>
                          <span className="text-gray-400">Version: </span>
                          {health.elasticsearch.version}
                        </p>
                      )}
                      {health.elasticsearch.error && (
                        <p className="text-red-400">{health.elasticsearch.error}</p>
                      )}
                    </>
                  )}
                </div>
              ) : (
                <p className="text-gray-400">Unable to fetch health</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
