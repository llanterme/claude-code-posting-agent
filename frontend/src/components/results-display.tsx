"use client";

import { useState } from "react";
import { 
  Copy, 
  Download, 
  FileText, 
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Target,
  Hash
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { useGenerationStore } from "@/lib/stores/generation-store";
import { useHistoryStore } from "@/lib/stores/history-store";
import { copyToClipboard, downloadTextFile, generateId, formatExecutionTime } from "@/lib/utils";
import { HistoryItem } from "@/lib/types";

export function ResultsDisplay() {
  const { generationState } = useGenerationStore();
  const { addHistoryItem } = useHistoryStore();
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const result = generationState.result;

  if (!result) {
    return null;
  }

  const handleCopy = async (text: string, field: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    }
  };

  const handleDownload = () => {
    const content = `Topic: ${result.topic}
Platform: ${result.platform}
Tone: ${result.tone}
Generated: ${new Date().toLocaleString()}
Execution Time: ${formatExecutionTime(result.execution_time_seconds)}

RESEARCH INSIGHTS:
${result.research_bullet_points.map((point, i) => `${i + 1}. ${point}`).join('\n')}

GENERATED CONTENT:
${result.generated_content}

Word Count: ${result.word_count}
${result.generated_image_path ? `Image: ${result.generated_image_path}` : ''}`;

    const filename = `content_${result.topic.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}.txt`;
    downloadTextFile(content, filename);
  };

  const handleSaveToHistory = () => {
    const historyItem: HistoryItem = {
      id: generateId(),
      timestamp: new Date().toISOString(),
      request: {
        topic: result.topic,
        platform: result.platform,
        tone: result.tone,
      },
      response: result,
    };
    addHistoryItem(historyItem);
  };

  const CopyButton = ({ text, field, label }: { text: string; field: string; label: string }) => (
    <Button
      variant="outline"
      size="sm"
      onClick={() => handleCopy(text, field)}
      className="h-8"
    >
      {copiedField === field ? (
        <CheckCircle2 className="h-3 w-3 mr-1" />
      ) : (
        <Copy className="h-3 w-3 mr-1" />
      )}
      {copiedField === field ? "Copied!" : label}
    </Button>
  );

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
              Generation Results
            </CardTitle>
            <CardDescription>
              Content generated for &quot;{result.topic}&quot;
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSaveToHistory} variant="outline" size="sm">
              Save to History
            </Button>
            <Button onClick={handleDownload} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1" />
              Download
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Metadata */}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Target className="h-4 w-4" />
            Platform: {result.platform}
          </div>
          <div className="flex items-center gap-1">
            <Hash className="h-4 w-4" />
            Tone: {result.tone}
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            {formatExecutionTime(result.execution_time_seconds)}
          </div>
          <div className="flex items-center gap-1">
            <FileText className="h-4 w-4" />
            {result.word_count} words
          </div>
        </div>

        {!result.success && result.error && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">Generation Error</span>
            </div>
            <p className="mt-1 text-sm">{result.error}</p>
          </div>
        )}

        <Tabs defaultValue="content" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="content">Generated Content</TabsTrigger>
            <TabsTrigger value="research">Research Insights</TabsTrigger>
            <TabsTrigger value="media">Media</TabsTrigger>
          </TabsList>

          <TabsContent value="content" className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Generated Content</h3>
                <CopyButton 
                  text={result.generated_content} 
                  field="content" 
                  label="Copy Content" 
                />
              </div>
              <Textarea
                value={result.generated_content}
                readOnly
                className="min-h-[200px] font-mono text-sm"
              />
              <div className="text-sm text-muted-foreground">
                {result.word_count} words
              </div>
            </div>
          </TabsContent>

          <TabsContent value="research" className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Research Insights</h3>
                <CopyButton 
                  text={result.research_bullet_points.join('\n')} 
                  field="research" 
                  label="Copy Research" 
                />
              </div>
              <div className="space-y-2">
                {result.research_bullet_points.map((point, index) => (
                  <div key={index} className="flex gap-2 p-3 bg-muted rounded-lg">
                    <Badge variant="outline" className="shrink-0">
                      {index + 1}
                    </Badge>
                    <p className="text-sm">{point}</p>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="media" className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Generated Media</h3>
              {result.generated_image_path ? (
                <div className="space-y-4">
                  <div className="relative rounded-lg border overflow-hidden">
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_URL}/${result.generated_image_path}`}
                      alt={`Generated image for ${result.topic}`}
                      className="w-full h-auto max-h-96 object-contain"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        target.nextElementSibling?.classList.remove('hidden');
                      }}
                    />
                    <div className="hidden p-8 text-center text-muted-foreground">
                      <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Image could not be loaded</p>
                      <p className="text-xs">{result.generated_image_path}</p>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Image path: {result.generated_image_path}</span>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        if (result.generated_image_path) {
                          const link = document.createElement('a');
                          link.href = `${process.env.NEXT_PUBLIC_API_URL}/${result.generated_image_path}`;
                          link.download = result.generated_image_path.split('/').pop() || 'image.png';
                          link.click();
                        }
                      }}
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Download Image
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                  <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No image was generated for this content</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}