"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Sparkles, History, Activity } from "lucide-react";

import { GenerationForm } from "@/components/generation-form";
import { ProgressTracker } from "@/components/progress-tracker";
import { ResultsDisplay } from "@/components/results-display";
import { HistoryGallery } from "@/components/history-gallery";
import { useGenerationStore } from "@/lib/stores/generation-store";

export default function Home() {
  const { generationState } = useGenerationStore();
  const [activeTab, setActiveTab] = useState("generate");

  // Keep user on current tab - they can manually switch to see results
  const handleGenerationSubmit = () => {
    // Don't auto-navigate - let user see progress on Generate tab
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Multi-Agent Content Generator
          </h1>
          <p className="text-lg text-muted-foreground mt-2 max-w-2xl mx-auto">
            AI-powered content generation with research, writing, and image creation
          </p>
          <div className="flex justify-center gap-2 mt-4">
            <Badge variant="secondary">Research Agent</Badge>
            <Badge variant="secondary">Content Agent</Badge>
            <Badge variant="secondary">Image Agent</Badge>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="generate" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Generate
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Results
              {generationState.result && (
                <Badge variant="outline" className="ml-1">
                  New
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="h-4 w-4" />
              History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-6">
            <div className="flex flex-col lg:flex-row gap-6 items-start">
              <div className="flex-1 w-full">
                <GenerationForm onSubmit={handleGenerationSubmit} />
              </div>
              <div className="flex-1 w-full">
                <ProgressTracker />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <div className="flex justify-center">
              {generationState.result ? (
                <ResultsDisplay />
              ) : (
                <Card className="w-full max-w-2xl">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      No Results Yet
                    </CardTitle>
                    <CardDescription>
                      Generate some content to see results here
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-8 text-muted-foreground">
                      <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Start by generating your first piece of content!</p>
                      <p className="text-sm mt-2">
                        Use the Generate tab to create AI-powered content with research and images.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <div className="flex justify-center">
              <HistoryGallery />
            </div>
          </TabsContent>
        </Tabs>

        {/* Error Display */}
        {generationState.error && (
          <Card className="mt-6 border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <span className="font-medium">Generation Error</span>
              </div>
              <p className="mt-2 text-sm">{generationState.error}</p>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-muted-foreground">
          <p>
            Powered by{" "}
            <span className="font-medium">PydanticAI</span>,{" "}
            <span className="font-medium">LangGraph</span>, and{" "}
            <span className="font-medium">OpenAI</span>
          </p>
        </footer>
      </div>
    </div>
  );
}
