"use client";

import { Search, PenTool, Image, CheckCircle, AlertCircle } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

import { useGenerationStore } from "@/lib/stores/generation-store";
import { cn } from "@/lib/utils";

const steps = [
  {
    id: "research",
    label: "Research",
    description: "Gathering information and creating bullet points",
    icon: Search,
  },
  {
    id: "content",
    label: "Content",
    description: "Writing platform-optimized content",
    icon: PenTool,
  },
  {
    id: "image",
    label: "Image",
    description: "Generating visual content",
    icon: Image,
  },
];

export function ProgressTracker() {
  const { generationState } = useGenerationStore();

  // Note: WebSocket lifecycle is managed by the generation process itself
  // No need to manage it in this component

  if (!generationState.isGenerating && !generationState.result) {
    return null;
  }

  const getCurrentStepIndex = () => {
    const currentStep = generationState.currentStep?.toLowerCase() || "";
    
    if (currentStep.includes("research")) return 0;
    if (currentStep.includes("content")) return 1;
    if (currentStep.includes("image")) return 2;
    if (generationState.progress === 100) return 3;
    
    return -1;
  };

  const currentStepIndex = getCurrentStepIndex();
  const hasError = !!generationState.error;

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Generation Progress</span>
          <Badge variant={hasError ? "destructive" : generationState.progress === 100 ? "default" : "secondary"}>
            {hasError ? "Error" : generationState.progress === 100 ? "Complete" : "In Progress"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{generationState.progress}%</span>
          </div>
          <Progress value={generationState.progress} className="h-2" />
        </div>

        {/* Current Step Message */}
        {generationState.currentStep && (
          <div className={cn(
            "p-3 rounded-lg text-sm",
            hasError 
              ? "bg-destructive/10 text-destructive" 
              : "bg-muted text-muted-foreground"
          )}>
            <div className="flex items-center gap-2">
              {hasError ? (
                <AlertCircle className="h-4 w-4" />
              ) : generationState.progress === 100 ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              )}
              {generationState.currentStep}
            </div>
            {generationState.error && (
              <div className="mt-2 text-xs">
                Error: {generationState.error}
              </div>
            )}
          </div>
        )}

        {/* Step Indicators */}
        <div className="space-y-3">
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex || generationState.progress === 100;
            const isCurrent = index === currentStepIndex && generationState.isGenerating;
            const isError = hasError && index === currentStepIndex;

            const StepIcon = step.icon;

            return (
              <div key={step.id} className="flex items-center gap-3">
                <div
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-full border-2 transition-colors",
                    isCompleted
                      ? "border-green-500 bg-green-500 text-white"
                      : isCurrent
                      ? "border-primary bg-primary text-primary-foreground"
                      : isError
                      ? "border-destructive bg-destructive text-destructive-foreground"
                      : "border-muted-foreground/20 bg-muted"
                  )}
                >
                  {isCompleted ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : isError ? (
                    <AlertCircle className="h-4 w-4" />
                  ) : (
                    <StepIcon className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "font-medium",
                        isCompleted || isCurrent
                          ? "text-foreground"
                          : "text-muted-foreground"
                      )}
                    >
                      {step.label}
                    </span>
                    {isCurrent && !isError && (
                      <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Execution Time */}
        {generationState.result && (
          <div className="pt-2 border-t">
            <div className="text-sm text-muted-foreground">
              Completed in {generationState.result.execution_time_seconds.toFixed(1)} seconds
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}