"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { Loader2, Sparkles, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { apiClient, queryKeys } from "@/lib/api";
import { FormData } from "@/lib/types";
import { useGenerationStore } from "@/lib/stores/generation-store";

const formSchema = z.object({
  topic: z
    .string()
    .min(3, "Topic must be at least 3 characters long")
    .max(100, "Topic must be less than 100 characters"),
  platform: z.string().min(1, "Please select a platform"),
  tone: z.string().min(1, "Please select a tone"),
});

interface GenerationFormProps {
  onSubmit?: (data: FormData) => void;
}

export function GenerationForm({ onSubmit }: GenerationFormProps) {
  const { generationState, startGeneration } = useGenerationStore();
  
  // Fetch platforms and tones
  const { data: platformsData, isLoading: loadingPlatforms, error: platformsError } = useQuery({
    queryKey: queryKeys.platforms,
    queryFn: apiClient.getPlatforms,
  });

  const { data: tonesData, isLoading: loadingTones, error: tonesError } = useQuery({
    queryKey: queryKeys.tones,
    queryFn: apiClient.getTones,
  });

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      topic: "",
      platform: "",
      tone: "",
    },
  });

  const handleSubmit = (data: FormData) => {
    startGeneration(data);
    onSubmit?.(data);
  };

  const isLoading = generationState.isGenerating || loadingPlatforms || loadingTones;
  const hasConnectionError = platformsError || tonesError;

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          Generate Content
        </CardTitle>
        <CardDescription>
          Create AI-powered content with research, writing, and image generation
        </CardDescription>
        {hasConnectionError && (
          <div className="mt-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex items-center gap-2 text-destructive text-sm">
              <AlertCircle className="h-4 w-4" />
              <span>Unable to connect to backend server. Please ensure the API server is running on http://localhost:8000</span>
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="topic"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Topic</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter your topic (e.g., artificial intelligence, climate change)"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormDescription>
                    What would you like to create content about?
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="platform"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Platform</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      disabled={isLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select platform" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="max-w-[300px]">
                        {platformsData?.platforms.map((platform) => (
                          <SelectItem key={platform.name} value={platform.name}>
                            <div className="flex flex-col">
                              <span className="font-medium">{platform.display_name}</span>
                              <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                                {platform.description}
                                {platform.max_length && ` (${platform.max_length} chars)`}
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="tone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tone</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      disabled={isLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select tone" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="max-w-[300px]">
                        {tonesData?.tones.map((tone) => (
                          <SelectItem key={tone.name} value={tone.name}>
                            <div className="flex flex-col">
                              <span className="font-medium">{tone.display_name}</span>
                              <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                                {tone.description}
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
              size="lg"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {generationState.currentStep || "Loading..."}
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Content
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}