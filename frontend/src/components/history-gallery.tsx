"use client";

import { useEffect, useState } from "react";
import { 
  Trash2, 
  Eye, 
  Calendar, 
  Target, 
  Hash, 
  FileText,
  Image as ImageIcon,
  Download,
  Copy,
  CheckCircle2
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { useHistoryStore } from "@/lib/stores/history-store";
import { formatTimestamp, truncateText, copyToClipboard, downloadTextFile, formatExecutionTime } from "@/lib/utils";
import { HistoryItem } from "@/lib/types";

export function HistoryGallery() {
  const { history, loadHistory, removeHistoryItem, clearHistory } = useHistoryStore();
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  // Load history from localStorage on mount
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleCopy = async (text: string, field: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    }
  };

  const handleDownload = (item: HistoryItem) => {
    const content = `Topic: ${item.response.topic}
Platform: ${item.response.platform}
Tone: ${item.response.tone}
Generated: ${formatTimestamp(item.timestamp)}
Execution Time: ${formatExecutionTime(item.response.execution_time_seconds)}

RESEARCH INSIGHTS:
${item.response.research_bullet_points.map((point, i) => `${i + 1}. ${point}`).join('\n')}

GENERATED CONTENT:
${item.response.generated_content}

Word Count: ${item.response.word_count}
${item.response.generated_image_path ? `Image: ${item.response.generated_image_path}` : ''}`;

    const filename = `content_${item.response.topic.replace(/\s+/g, '_').toLowerCase()}_${new Date(item.timestamp).getTime()}.txt`;
    downloadTextFile(content, filename);
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

  if (history.length === 0) {
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Generation History</CardTitle>
          <CardDescription>
            Your previously generated content will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No generation history yet</p>
            <p className="text-sm">Generate some content to see it here!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Generation History</CardTitle>
            <CardDescription>
              {history.length} generation{history.length !== 1 ? 's' : ''} saved
            </CardDescription>
          </div>
          <Button
            variant="destructive"
            size="sm"
            onClick={clearHistory}
            disabled={history.length === 0}
          >
            <Trash2 className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {history.map((item) => (
            <Card key={item.id} className="relative">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-base truncate">
                      {item.response.topic}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {formatTimestamp(item.timestamp)}
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="ml-2 shrink-0"
                    onClick={() => removeHistoryItem(item.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                <div className="flex flex-wrap gap-1">
                  <Badge variant="secondary" className="text-xs">
                    {item.response.platform}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {item.response.tone}
                  </Badge>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-3">
                  {truncateText(item.response.generated_content, 100)}
                </p>

                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <FileText className="h-3 w-3" />
                  {item.response.word_count} words
                  {item.response.generated_image_path && (
                    <>
                      <ImageIcon className="h-3 w-3" />
                      Image
                    </>
                  )}
                </div>

                <div className="flex gap-1">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => setSelectedItem(item)}
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                      {selectedItem && (
                        <>
                          <DialogHeader>
                            <DialogTitle>{selectedItem.response.topic}</DialogTitle>
                            <DialogDescription>
                              Generated on {formatTimestamp(selectedItem.timestamp)}
                            </DialogDescription>
                          </DialogHeader>

                          <div className="space-y-4">
                            {/* Metadata */}
                            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Target className="h-4 w-4" />
                                Platform: {selectedItem.response.platform}
                              </div>
                              <div className="flex items-center gap-1">
                                <Hash className="h-4 w-4" />
                                Tone: {selectedItem.response.tone}
                              </div>
                              <div className="flex items-center gap-1">
                                <Calendar className="h-4 w-4" />
                                {formatExecutionTime(selectedItem.response.execution_time_seconds)}
                              </div>
                              <div className="flex items-center gap-1">
                                <FileText className="h-4 w-4" />
                                {selectedItem.response.word_count} words
                              </div>
                            </div>

                            <Tabs defaultValue="content" className="w-full">
                              <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger value="content">Content</TabsTrigger>
                                <TabsTrigger value="research">Research</TabsTrigger>
                                <TabsTrigger value="media">Media</TabsTrigger>
                              </TabsList>

                              <TabsContent value="content" className="space-y-4">
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between">
                                    <h3 className="text-lg font-semibold">Generated Content</h3>
                                    <CopyButton 
                                      text={selectedItem.response.generated_content} 
                                      field="content" 
                                      label="Copy" 
                                    />
                                  </div>
                                  <Textarea
                                    value={selectedItem.response.generated_content}
                                    readOnly
                                    className="min-h-[200px] font-mono text-sm"
                                  />
                                </div>
                              </TabsContent>

                              <TabsContent value="research" className="space-y-4">
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between">
                                    <h3 className="text-lg font-semibold">Research Insights</h3>
                                    <CopyButton 
                                      text={selectedItem.response.research_bullet_points.join('\n')} 
                                      field="research" 
                                      label="Copy" 
                                    />
                                  </div>
                                  <div className="space-y-2">
                                    {selectedItem.response.research_bullet_points.map((point, index) => (
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
                                  {selectedItem.response.generated_image_path ? (
                                    <div className="space-y-4">
                                      <div className="relative rounded-lg border overflow-hidden">
                                        <img
                                          src={`${process.env.NEXT_PUBLIC_API_URL}/${selectedItem.response.generated_image_path}`}
                                          alt={`Generated image for ${selectedItem.response.topic}`}
                                          className="w-full h-auto max-h-96 object-contain"
                                        />
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                                      <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
                                      <p>No image was generated</p>
                                    </div>
                                  )}
                                </div>
                              </TabsContent>
                            </Tabs>

                            <div className="flex justify-end">
                              <Button onClick={() => handleDownload(selectedItem)} variant="outline">
                                <Download className="h-4 w-4 mr-1" />
                                Download
                              </Button>
                            </div>
                          </div>
                        </>
                      )}
                    </DialogContent>
                  </Dialog>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(item)}
                  >
                    <Download className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}