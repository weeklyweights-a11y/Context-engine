import { api } from "./api";
import type { ApiResponse } from "../types/common";
import type {
  OnboardingStatus,
  ProductContext,
  WizardSection,
  WizardSectionData,
} from "../types/product";

const PREFIX = "/product";

/** Get onboarding status. */
export async function getOnboardingStatus(): Promise<OnboardingStatus> {
  const { data } = await api.get<ApiResponse<OnboardingStatus>>(
    `${PREFIX}/onboarding-status`
  );
  return data.data;
}

/** Mark onboarding complete. */
export async function markOnboardingComplete(): Promise<{ completed: boolean }> {
  const { data } = await api.post<ApiResponse<{ completed: boolean }>>(
    `${PREFIX}/onboarding-complete`
  );
  return data.data;
}

/** Get all wizard sections. */
export async function getWizardAll(): Promise<{
  data: Record<string, Record<string, unknown>>;
  completed_sections: string[];
}> {
  const { data } = await api.get<
    ApiResponse<{
      data: Record<string, Record<string, unknown>>;
      completed_sections: string[];
    }>
  >(`${PREFIX}/wizard`);
  return data.data;
}

/** Get one wizard section. Returns doc with section, data, etc. */
export async function getWizardSection(
  section: WizardSection
): Promise<{ section: string; data: Record<string, unknown> } | null> {
  try {
    const { data } = await api.get<
      ApiResponse<{ section: string; data: Record<string, unknown> }>
    >(`${PREFIX}/wizard/${section}`);
    return data.data;
  } catch (err: unknown) {
    if (
      err &&
      typeof err === "object" &&
      "response" in err &&
      err.response &&
      typeof err.response === "object" &&
      "status" in err.response &&
      err.response.status === 404
    ) {
      return null;
    }
    throw err;
  }
}

/** Save or update one wizard section. */
export async function putWizardSection(
  section: WizardSection,
  body: WizardSectionData
): Promise<{ data: Record<string, unknown> }> {
  const { data } = await api.put<
    ApiResponse<{ data: Record<string, unknown> }>
  >(`${PREFIX}/wizard/${section}`, body as unknown as Record<string, unknown>);
  return data.data;
}

/** Delete one wizard section. */
export async function deleteWizardSection(
  section: WizardSection
): Promise<void> {
  await api.delete(`${PREFIX}/wizard/${section}`);
}

/** Get flattened product context. */
export async function getProductContext(): Promise<ProductContext> {
  const { data } = await api.get<ApiResponse<ProductContext>>(
    `${PREFIX}/context`
  );
  return data.data;
}
