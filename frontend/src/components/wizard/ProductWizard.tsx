import { useState, useEffect, useCallback } from "react";
import { getWizardAll, putWizardSection } from "../../services/productApi";
import {
  WIZARD_SECTIONS,
  type WizardSection,
  type WizardSectionData,
} from "../../types/product";
import WizardStepBasics from "./WizardStepBasics";
import WizardStepAreas from "./WizardStepAreas";
import WizardStepGoals from "./WizardStepGoals";
import WizardStepSegments from "./WizardStepSegments";
import WizardStepCompetitors from "./WizardStepCompetitors";
import WizardStepRoadmap from "./WizardStepRoadmap";
import WizardStepTeams from "./WizardStepTeams";
import WizardStepTechStack from "./WizardStepTechStack";

const STEP_LABELS: Record<WizardSection, string> = {
  basics: "Product basics",
  areas: "Product areas",
  goals: "Goals",
  segments: "Segments & pricing",
  competitors: "Competitors",
  roadmap: "Roadmap",
  teams: "Teams",
  tech_stack: "Tech stack",
};

interface ProductWizardProps {
  mode: "onboarding" | "settings";
  onComplete?: () => void;
}

export default function ProductWizard({ mode, onComplete }: ProductWizardProps) {
  const [activeSection, setActiveSection] = useState<WizardSection>("basics");
  const [sectionsData, setSectionsData] = useState<
    Record<string, Record<string, unknown>>
  >({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getWizardAll();
      setSectionsData(res.data ?? {});
    } catch {
      setSectionsData({});
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);


  const handleSave = useCallback(
    async (section: WizardSection, data: WizardSectionData) => {
      setSaving(true);
      try {
        await putWizardSection(section, data);
        await fetchAll();
      } finally {
        setSaving(false);
      }
    },
    [fetchAll]
  );

  const handleSectionSave = useCallback(
    (section: WizardSection) => async (data: WizardSectionData) => {
      await handleSave(section, data);
      if (mode === "onboarding") {
        const idx = WIZARD_SECTIONS.indexOf(section);
        if (idx < WIZARD_SECTIONS.length - 1) {
          setStepIndex(idx + 1);
          setActiveSection(WIZARD_SECTIONS[idx + 1]);
        }
      }
    },
    [handleSave, mode]
  );

  const handleSkip = useCallback(() => {
    if (mode === "onboarding" && stepIndex < WIZARD_SECTIONS.length - 1) {
      setStepIndex(stepIndex + 1);
      setActiveSection(WIZARD_SECTIONS[stepIndex + 1]);
    }
  }, [mode, stepIndex]);

  const handleBack = useCallback(() => {
    if (stepIndex > 0) {
      setStepIndex(stepIndex - 1);
      setActiveSection(WIZARD_SECTIONS[stepIndex - 1]);
    }
  }, [stepIndex]);

  const completedCount = Object.keys(sectionsData).filter(
    (k) => sectionsData[k] && Object.keys(sectionsData[k]).length > 0
  ).length;

  if (loading) {
    return (
      <div className="text-gray-400 py-8">Loading wizard data...</div>
    );
  }

  if (mode === "settings") {
    return (
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2 border-b border-gray-700 pb-3">
          {WIZARD_SECTIONS.map((sec) => (
            <button
              key={sec}
              onClick={() => setActiveSection(sec)}
              className={`px-3 py-1.5 rounded-lg text-sm ${
                activeSection === sec
                  ? "bg-blue-500 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-gray-100"
              }`}
            >
              {STEP_LABELS[sec]}
            </button>
          ))}
        </div>
        <div className="pt-2">
          <h3 className="text-gray-100 font-medium mb-3">
            {STEP_LABELS[activeSection]}
          </h3>
          <WizardStepContent
            section={activeSection}
            initialData={sectionsData[activeSection]}
            onSave={handleSectionSave(activeSection)}
            saving={saving}
          />
        </div>
      </div>
    );
  }

  // Onboarding mode: linear flow
  const currentSection = WIZARD_SECTIONS[stepIndex];
  const progress = ((stepIndex + 1) / WIZARD_SECTIONS.length) * 100;

  return (
    <div className="space-y-6">
      <div>
        <div className="flex justify-between text-sm text-gray-400 mb-1">
          <span>
            Step {stepIndex + 1} of {WIZARD_SECTIONS.length}
          </span>
          <span>{completedCount} sections completed</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      <h3 className="text-gray-100 font-medium text-lg">
        {STEP_LABELS[currentSection]}
      </h3>
          <WizardStepContent
        section={currentSection}
        initialData={sectionsData[currentSection]}
        onSave={handleSectionSave(currentSection)}
        saving={saving}
        submitLabel="Continue"
      />
      <div className="flex justify-between pt-4">
        <button
          type="button"
          onClick={handleBack}
          disabled={stepIndex === 0}
          className="px-4 py-2 text-gray-400 hover:text-gray-100 disabled:opacity-50"
        >
          Back
        </button>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleSkip}
            className="px-4 py-2 text-gray-400 hover:text-gray-100"
          >
            Skip
          </button>
          {stepIndex === WIZARD_SECTIONS.length - 1 ? (
            <button
              type="button"
              onClick={onComplete}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Finish
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

interface WizardStepContentProps {
  section: WizardSection;
  initialData?: Record<string, unknown>;
  onSave: (data: WizardSectionData) => Promise<void>;
  saving: boolean;
  submitLabel?: "Save" | "Continue";
}

function WizardStepContent({
  section,
  initialData,
  onSave,
  saving,
  submitLabel = "Save",
}: WizardStepContentProps) {
  const common = { initialData, onSave, saving, submitLabel };
  switch (section) {
    case "basics":
      return (
        <WizardStepBasics
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductBasics>}
        />
      );
    case "areas":
      return (
        <WizardStepAreas
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductAreas>}
        />
      );
    case "goals":
      return (
        <WizardStepGoals
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductGoals>}
        />
      );
    case "segments":
      return (
        <WizardStepSegments
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductSegments>}
        />
      );
    case "competitors":
      return (
        <WizardStepCompetitors
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductCompetitors>}
        />
      );
    case "roadmap":
      return (
        <WizardStepRoadmap
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductRoadmap>}
        />
      );
    case "teams":
      return (
        <WizardStepTeams
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductTeams>}
        />
      );
    case "tech_stack":
      return (
        <WizardStepTechStack
          {...common}
          initialData={initialData as Partial<import("../../types/product").ProductTechStack>}
        />
      );
    default:
      return null;
  }
}
