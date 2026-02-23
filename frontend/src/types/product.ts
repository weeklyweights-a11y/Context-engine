/** Product wizard section names. */
export const WIZARD_SECTIONS = [
  "basics",
  "areas",
  "goals",
  "segments",
  "competitors",
  "roadmap",
  "teams",
  "tech_stack",
] as const;

export type WizardSection = (typeof WIZARD_SECTIONS)[number];

/** Product basics (step 1). */
export interface ProductBasics {
  product_name: string;
  description?: string;
  industry?: string;
  stage?: string;
  website_url?: string;
}

/** Single product area. */
export interface ProductArea {
  name: string;
  description?: string;
  id?: string;
  order?: number;
}

/** Product areas (step 2). */
export interface ProductAreas {
  areas: ProductArea[];
}

/** Single goal/OKR. */
export interface Goal {
  time_period?: string;
  title: string;
  description?: string;
  priority?: "P0" | "P1" | "P2" | "P3";
  linked_area_id?: string;
  id?: string;
}

/** Business goals (step 3). */
export interface ProductGoals {
  goals: Goal[];
}

/** Customer segment. */
export interface Segment {
  name: string;
  description?: string;
  revenue_share?: number;
  id?: string;
}

/** Pricing tier. */
export interface PricingTier {
  name: string;
  price?: number;
  price_period?: string;
  segment_id?: string;
  features?: string;
  id?: string;
}

/** Segments and pricing (step 4). */
export interface ProductSegments {
  segments: Segment[];
  pricing_tiers: PricingTier[];
}

/** Competitor entry. */
export interface Competitor {
  name: string;
  website?: string;
  strengths?: string;
  weaknesses?: string;
  differentiation?: string;
  id?: string;
}

/** Competitors (step 5). */
export interface ProductCompetitors {
  competitors: Competitor[];
}

/** Existing/live feature. */
export interface ExistingFeature {
  name: string;
  area_id?: string;
  status?: "live" | "beta" | "deprecated";
  release_date?: string;
  id?: string;
}

/** Planned feature. */
export interface PlannedFeature {
  name: string;
  area_id?: string;
  status?: "planned" | "in_progress" | "blocked";
  target_date?: string;
  priority?: string;
  id?: string;
}

/** Roadmap (step 6). */
export interface ProductRoadmap {
  existing_features: ExistingFeature[];
  planned_features: PlannedFeature[];
}

/** Team entry. */
export interface Team {
  name: string;
  lead?: string;
  area_ids?: string[];
  size?: number;
  slack_channel?: string;
  id?: string;
}

/** Teams (step 7). */
export interface ProductTeams {
  teams: Team[];
}

/** Tech stack entry. */
export interface TechItem {
  category?:
    | "Frontend"
    | "Backend"
    | "Database"
    | "Infrastructure"
    | "Monitoring"
    | "Other";
  technology: string;
  notes?: string;
  id?: string;
}

/** Tech stack (step 8). */
export interface ProductTechStack {
  technologies: TechItem[];
}

/** Union of all wizard section payloads. */
export type WizardSectionData =
  | ProductBasics
  | ProductAreas
  | ProductGoals
  | ProductSegments
  | ProductCompetitors
  | ProductRoadmap
  | ProductTeams
  | ProductTechStack;

/** Onboarding status. */
export interface OnboardingStatus {
  completed: boolean;
  completed_sections: string[];
  total_sections: number;
}

/** Flattened product context for agent. */
export interface ProductContext {
  product_name?: string;
  description?: string;
  industry?: string;
  stage?: string;
  website_url?: string;
  areas?: Record<string, unknown>[];
  goals?: Record<string, unknown>[];
  segments?: Record<string, unknown>[];
  pricing_tiers?: Record<string, unknown>[];
  competitors?: Record<string, unknown>[];
  existing_features?: Record<string, unknown>[];
  planned_features?: Record<string, unknown>[];
  teams?: Record<string, unknown>[];
  technologies?: Record<string, unknown>[];
}
