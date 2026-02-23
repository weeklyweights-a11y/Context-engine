import { useState, useEffect, useCallback } from "react";
import {
  getOnboardingStatus,
  markOnboardingComplete,
} from "../services/productApi";
import type { OnboardingStatus } from "../types/product";

export function useOnboardingStatus() {
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const s = await getOnboardingStatus();
      setStatus(s);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load onboarding status");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const complete = useCallback(async () => {
    try {
      await markOnboardingComplete();
      await fetchStatus();
    } catch (e) {
      throw e instanceof Error ? e : new Error("Failed to complete onboarding");
    }
  }, [fetchStatus]);

  return {
    status,
    loading,
    error,
    refetch: fetchStatus,
    complete,
  };
}
