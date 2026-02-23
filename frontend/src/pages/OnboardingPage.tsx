import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useOnboardingStatus } from "../hooks/useOnboardingStatus";
import ProductWizard from "../components/wizard/ProductWizard";
import FeedbackUpload from "../components/upload/FeedbackUpload";
import CustomerUpload from "../components/upload/CustomerUpload";

type Step = "welcome" | "product" | "feedback" | "customers";

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { status, loading, error, complete } = useOnboardingStatus();
  const [activeStep, setActiveStep] = useState<Step>("welcome");
  const [productDone, setProductDone] = useState(false);
  const [feedbackDone, setFeedbackDone] = useState(false);
  const [showComplete, setShowComplete] = useState(false);

  const handleProductComplete = async () => {
    try {
      await complete();
      setProductDone(true);
      setActiveStep("feedback");
    } catch {
      // Error handling in useOnboardingStatus
    }
  };

  const handleFeedbackDone = () => {
    setFeedbackDone(true);
    setActiveStep("customers");
  };

  const handleCustomersDone = () => {
    setShowComplete(true);
  };

  const handleSkipAll = async () => {
    try {
      await complete();
      navigate("/dashboard");
    } catch {
      // Error handling
    }
  };

  const handleGoToDashboard = () => {
    navigate("/dashboard");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  if (status?.completed && !showComplete && !productDone) {
    navigate("/dashboard", { replace: true });
    return null;
  }

  if (showComplete) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-8">
        <div className="max-w-lg text-center space-y-6">
          <h1 className="text-3xl font-bold text-gray-100">Setup complete!</h1>
          <p className="text-gray-400">
            Your product context, feedback, and customers are ready. You can always add more in
            Settings.
          </p>
          <button
            onClick={handleGoToDashboard}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (activeStep === "product" && !productDone) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-6 flex gap-2">
            <button
              type="button"
              onClick={() => setActiveStep("product")}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              ← Back
            </button>
            <span className="text-gray-500 text-sm">Step 1 of 3: Product Setup</span>
          </div>
          <ProductWizard mode="onboarding" onComplete={handleProductComplete} />
        </div>
      </div>
    );
  }

  if (activeStep === "feedback") {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-6 flex gap-4">
            <button
              type="button"
              onClick={() => setActiveStep("product")}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              ← Back
            </button>
            <span className="text-gray-500 text-sm">Step 2 of 3: Upload Feedback</span>
          </div>
          <FeedbackUpload />
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={handleFeedbackDone}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Continue to Customers
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="px-4 py-2 text-gray-400 hover:text-gray-300"
            >
              Skip to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (activeStep === "customers") {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-6 flex gap-4">
            <button
              type="button"
              onClick={() => setActiveStep("feedback")}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              ← Back
            </button>
            <span className="text-gray-500 text-sm">Step 3 of 3: Upload Customers</span>
          </div>
          <CustomerUpload />
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={handleCustomersDone}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Finish Setup → Go to Dashboard
            </button>
            <button
              type="button"
              onClick={handleSkipAll}
              className="px-4 py-2 text-gray-400 hover:text-gray-300"
            >
              Skip to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8">
        <h1 className="text-3xl font-bold text-gray-100 text-center">
          Welcome to Context Engine!
        </h1>
        <p className="text-gray-400 text-center">
          Let&apos;s set up your product.
        </p>
          <div className="grid grid-cols-3 gap-4">
            <button
              onClick={() => { setActiveStep("product"); }}
            className="p-6 rounded-lg bg-blue-500/20 border-2 border-blue-500 text-left hover:bg-blue-500/30 transition-colors"
          >
            <h3 className="font-semibold text-gray-100 mb-1">1. Product Setup</h3>
            <p className="text-sm text-gray-400">Define your product areas, goals, and context</p>
          </button>
          <button
            onClick={() => productDone && setActiveStep("feedback")}
            className={`p-6 rounded-lg text-left transition-colors ${
              productDone
                ? "bg-blue-500/20 border-2 border-blue-500 hover:bg-blue-500/30 cursor-pointer"
                : "bg-gray-800/50 border border-gray-700 opacity-60 cursor-not-allowed"
            }`}
          >
            <h3
              className={`font-semibold mb-1 ${productDone ? "text-gray-100" : "text-gray-500"}`}
            >
              2. Upload Feedback
            </h3>
            <p className={`text-sm ${productDone ? "text-gray-400" : "text-gray-500"}`}>
              {productDone ? "CSV or manual entry" : "Complete Product Setup first"}
            </p>
          </button>
          <button
            onClick={() => feedbackDone && setActiveStep("customers")}
            className={`p-6 rounded-lg text-left transition-colors ${
              feedbackDone
                ? "bg-blue-500/20 border-2 border-blue-500 hover:bg-blue-500/30 cursor-pointer"
                : "bg-gray-800/50 border border-gray-700 opacity-60 cursor-not-allowed"
            }`}
          >
            <h3
              className={`font-semibold mb-1 ${feedbackDone ? "text-gray-100" : "text-gray-500"}`}
            >
              3. Upload Customers
            </h3>
            <p className={`text-sm ${feedbackDone ? "text-gray-400" : "text-gray-500"}`}>
              {feedbackDone ? "CSV or manual entry" : "Complete Feedback first"}
            </p>
          </button>
        </div>
        <p className="text-center">
          <button
            onClick={handleSkipAll}
            className="text-blue-400 hover:text-blue-300 underline"
          >
            Skip everything and explore
          </button>
        </p>
      </div>
    </div>
  );
}
