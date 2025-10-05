"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles, FileText, Download } from "lucide-react";

interface FRAGOBuilderProps {
  unitId: string;
  unitName: string;
  soldierIds: string[];
  reports: any[];
  suggestionId?: string | null;
}

interface FRAGOFields {
  situation: string;
  mission: string;
  execution: string;
  service_support: string;
  command_signal: string;
}

export function FRAGOBuilder({
  unitId,
  unitName,
  soldierIds,
  reports,
  suggestionId,
}: FRAGOBuilderProps) {
  const [loading, setLoading] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [fields, setFields] = useState<FRAGOFields>({
    situation: "",
    mission: "",
    execution: "",
    service_support: "",
    command_signal: "",
  });
  const [generatedDoc, setGeneratedDoc] = useState<string>("");
  const [fragoNumber, setFragoNumber] = useState<number | null>(null);

  const handleSuggest = async () => {
    setSuggesting(true);
    try {
      const response = await fetch(
        "https://military-hierarchy-backend.onrender.com/frago/suggest",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            unit_id: unitId,
            unit_name: unitName,
            soldier_ids: soldierIds,
            reports: reports,
            suggestion_id: suggestionId,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to get FRAGO suggestion");

      const data = await response.json();
      setFields(data.suggested_fields);
    } catch (error) {
      console.error("Error getting FRAGO suggestion:", error);
      alert("Failed to get AI suggestion. Please try again.");
    } finally {
      setSuggesting(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // Get all report IDs
      const reportIds = reports.map((r) => r.report_id).filter(Boolean);

      const response = await fetch(
        "https://military-hierarchy-backend.onrender.com/frago/generate",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            unit_id: unitId,
            unit_name: unitName,
            frago_fields: fields,
            source_report_ids: reportIds,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to generate FRAGO");

      const data = await response.json();
      setGeneratedDoc(data.formatted_document);
      setFragoNumber(data.frago_number);
    } catch (error) {
      console.error("Error generating FRAGO:", error);
      alert("Failed to generate FRAGO. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedDoc) return;

    const blob = new Blob([generatedDoc], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `FRAGO_${fragoNumber
      ?.toString()
      .padStart(4, "0")}_${unitName.replace(/\s+/g, "_")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const updateField = (field: keyof FRAGOFields, value: string) => {
    setFields((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border overflow-hidden">
      <div className="flex-shrink-0 border-b border-border p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-green-500" />
            <div>
              <h2 className="text-sm font-bold font-mono text-foreground tracking-wider">
                FRAGMENTARY ORDER (FRAGO)
              </h2>
              <p className="text-xs text-muted-foreground">
                {unitName} - {reports.length} reports
              </p>
            </div>
          </div>
          <div className="flex gap-1">
            <Button
              onClick={handleSuggest}
              disabled={suggesting || reports.length === 0}
              size="sm"
              variant="outline"
              className="h-7 text-xs"
            >
              <Sparkles className="h-3 w-3 mr-1" />
              {suggesting ? "Analyzing..." : "AI Suggest"}
            </Button>
            <Button
              onClick={handleGenerate}
              disabled={loading || !fields.mission}
              size="sm"
              className="h-7 text-xs bg-primary hover:bg-primary/90"
            >
              <FileText className="h-3 w-3 mr-1" />
              {loading ? "Generating..." : "Generate FRAGO"}
            </Button>
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
        {/* 1. SITUATION */}
        <div className="space-y-1">
          <Label
            htmlFor="situation"
            className="text-xs font-mono text-muted-foreground font-bold"
          >
            1. SITUATION
          </Label>
          <Textarea
            id="situation"
            value={fields.situation}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              updateField("situation", e.target.value);
            }}
            placeholder="Enemy/friendly forces..."
            className="font-mono text-xs resize-none overflow-y-auto max-h-[120px] bg-background/50"
            rows={2}
          />
        </div>
        {/* 2. MISSION */}
        <div className="space-y-1">
          <Label
            htmlFor="mission"
            className="text-xs font-mono text-muted-foreground font-bold"
          >
            2. MISSION
          </Label>
          <Textarea
            id="mission"
            value={fields.mission}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              updateField("mission", e.target.value);
            }}
            placeholder="Task and purpose..."
            className="font-mono text-xs resize-none overflow-y-auto max-h-[120px] bg-background/50"
            rows={2}
          />
        </div>{" "}
        {/* 3. EXECUTION */}
        <div className="space-y-1">
          <Label
            htmlFor="execution"
            className="text-xs font-mono text-muted-foreground font-bold"
          >
            3. EXECUTION
          </Label>
          <Textarea
            id="execution"
            value={fields.execution}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              updateField("execution", e.target.value);
            }}
            placeholder="Concept of operations..."
            className="font-mono text-xs resize-none overflow-y-auto max-h-[120px] bg-background/50"
            rows={3}
          />
        </div>{" "}
        {/* 4. SERVICE & SUPPORT */}
        <div className="space-y-1">
          <Label
            htmlFor="service_support"
            className="text-xs font-mono text-muted-foreground font-bold"
          >
            4. SERVICE & SUPPORT
          </Label>
          <Textarea
            id="service_support"
            value={fields.service_support}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              updateField("service_support", e.target.value);
            }}
            placeholder="Logistics..."
            className="font-mono text-xs resize-none overflow-y-auto max-h-[120px] bg-background/50"
            rows={2}
          />
        </div>{" "}
        {/* 5. COMMAND & SIGNAL */}
        <div className="space-y-1">
          <Label
            htmlFor="command_signal"
            className="text-xs font-mono text-muted-foreground font-bold"
          >
            5. COMMAND & SIGNAL
          </Label>
          <Textarea
            id="command_signal"
            value={fields.command_signal}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              updateField("command_signal", e.target.value);
            }}
            placeholder="Command & signal..."
            className="font-mono text-xs resize-none overflow-y-auto max-h-[120px] bg-background/50"
            rows={2}
          />
        </div>
        {/* Preview */}
        {generatedDoc && (
          <div className="border border-border rounded-md bg-card/30 p-3">
            <div className="flex items-center justify-between mb-2">
              <Label className="text-xs font-mono text-foreground">
                FRAGO {fragoNumber?.toString().padStart(4, "0")} - Preview
              </Label>
              <Button
                onClick={handleDownload}
                size="sm"
                variant="outline"
                className="h-6 text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                Download
              </Button>
            </div>
            <pre className="text-xs font-mono text-foreground/80 whitespace-pre-wrap overflow-x-auto">
              {generatedDoc}
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
}
