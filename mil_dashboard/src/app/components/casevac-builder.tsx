"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, Download, Sparkles, AlertTriangle } from "lucide-react";
import axios from "axios";

interface CASEVACBuilderProps {
  unitId: string;
  unitName: string;
  soldierIds: string[];
  reports: any[];
  suggestionId?: string | null;
}

interface CASEVACFields {
  location: string;
  callsign_frequency: string;
  precedence: string;
  special_equipment: string;
  patients: string;
  security: string;
  marking_method: string;
  nationality: string;
  nbc_contamination: string;
}

export function CASEVACBuilder({
  unitId,
  unitName,
  soldierIds,
  reports,
  suggestionId,
}: CASEVACBuilderProps) {
  const [fields, setFields] = useState<CASEVACFields>({
    location: "",
    callsign_frequency: "",
    precedence: "A",
    special_equipment: "A",
    patients: "",
    security: "N",
    marking_method: "D",
    nationality: "A",
    nbc_contamination: "N",
  });

  const [loading, setLoading] = useState(false);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState("");
  const [casevacNumber, setCasevacNumber] = useState<number | null>(null);

  // Auto-download when CASEVAC is generated
  useEffect(() => {
    if (generatedDoc && casevacNumber) {
      handleDownload();
    }
  }, [generatedDoc, casevacNumber]);

  const handleSuggest = async () => {
    setSuggestLoading(true);
    try {
      const response = await axios.post(
        "https://military-hierarchy-backend.onrender.com/casevac/suggest",
        {
          unit_id: unitId,
          unit_name: unitName,
          soldier_ids: soldierIds,
          reports: reports,
          suggestion_id: suggestionId,
        }
      );

      const suggested = response.data.suggested_fields;
      setFields({
        location: suggested.location || "",
        callsign_frequency: suggested.callsign_frequency || "",
        precedence: suggested.precedence || "A",
        special_equipment: suggested.special_equipment || "A",
        patients: suggested.patients || "",
        security: suggested.security || "N",
        marking_method: suggested.marking_method || "D",
        nationality: suggested.nationality || "A",
        nbc_contamination: suggested.nbc_contamination || "N",
      });
    } catch (error: any) {
      console.error("Error getting AI suggestions:", error);
      const errorMsg =
        error.response?.data?.detail || error.message || "Unknown error";
      alert(
        `Failed to get AI suggestions: ${errorMsg}\n\nPlease fill in manually.`
      );
    } finally {
      setSuggestLoading(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const sourceReportIds = reports.map((r) => r.report_id);

      const response = await axios.post(
        "https://military-hierarchy-backend.onrender.com/casevac/generate",
        {
          unit_id: unitId,
          unit_name: unitName,
          casevac_fields: fields,
          source_report_ids: sourceReportIds,
        }
      );

      setGeneratedDoc(response.data.formatted_document);
      setCasevacNumber(response.data.casevac_number);
    } catch (error: any) {
      console.error("Error generating CASEVAC:", error);
      const errorMsg =
        error.response?.data?.detail || error.message || "Unknown error";
      alert(`Failed to generate CASEVAC: ${errorMsg}`);
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
    a.download = `CASEVAC_${casevacNumber
      ?.toString()
      .padStart(4, "0")}_${unitName.replace(/\s+/g, "_")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const updateField = (key: keyof CASEVACFields, value: string) => {
    setFields((prev) => ({ ...prev, [key]: value }));
  };

  // Precedence options
  const precedenceOptions = [
    {
      value: "A",
      label: "A - URGENT",
      desc: "Life, limb, or eyesight threatening",
    },
    {
      value: "B",
      label: "B - URGENT-SURGICAL",
      desc: "Surgical intervention required",
    },
    {
      value: "C",
      label: "C - PRIORITY",
      desc: "Stable but needs medical care",
    },
    { value: "D", label: "D - ROUTINE", desc: "Minor injuries" },
    { value: "E", label: "E - CONVENIENCE", desc: "Non-urgent" },
  ];

  // Special Equipment options
  const equipmentOptions = [
    { value: "A", label: "A - None" },
    { value: "B", label: "B - Hoist" },
    { value: "C", label: "C - Extraction Equipment" },
    { value: "D", label: "D - Ventilator" },
  ];

  // Security options
  const securityOptions = [
    { value: "N", label: "N - No enemy in area" },
    { value: "P", label: "P - Possible enemy" },
    { value: "E", label: "E - Enemy in area (armed escort)" },
    { value: "X", label: "X - Armed escort required" },
  ];

  // Marking Method options
  const markingOptions = [
    { value: "A", label: "A - Panels" },
    { value: "B", label: "B - Pyrotechnic signal" },
    { value: "C", label: "C - Smoke signal" },
    { value: "D", label: "D - None" },
    { value: "E", label: "E - Other" },
  ];

  // Nationality options
  const nationalityOptions = [
    { value: "A", label: "A - US Military" },
    { value: "B", label: "B - US Civilian" },
    { value: "C", label: "C - Non-US Military" },
    { value: "D", label: "D - Non-US Civilian" },
    { value: "E", label: "E - EPW (Enemy Prisoner of War)" },
  ];

  return (
    <Card className="h-full flex flex-col bg-card/50 backdrop-blur-sm border-border overflow-hidden">
      <div className="flex-shrink-0 p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          <div>
            <h2 className="text-sm font-bold font-mono text-foreground tracking-wider">
              CASEVAC REQUEST (9-LINE)
            </h2>
            <p className="text-xs text-muted-foreground">
              Medical Evacuation Request for {unitName}
            </p>
          </div>
        </div>
        <Button
          onClick={handleSuggest}
          disabled={suggestLoading || reports.length === 0}
          size="sm"
          className="h-7 text-xs bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50"
        >
          {suggestLoading ? (
            <>
              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="h-3 w-3 mr-1" />
              AI Suggest
            </>
          )}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
        {/* Line 1: Location */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 1: LOCATION (Grid Coordinates)
          </Label>
          <Textarea
            value={fields.location}
            onChange={(e) => updateField("location", e.target.value)}
            placeholder="e.g., NV123456 or 38.8977°N, 77.0365°W"
            className="font-mono text-sm resize-none max-h-[100px] overflow-y-auto bg-background/50"
            rows={1}
          />
        </div>

        {/* Line 2: Callsign/Frequency */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 2: RADIO FREQUENCY/CALLSIGN
          </Label>
          <Textarea
            value={fields.callsign_frequency}
            onChange={(e) => updateField("callsign_frequency", e.target.value)}
            placeholder="e.g., 30.55 MHz / DUSTOFF 23"
            className="font-mono text-sm resize-none max-h-[100px] overflow-y-auto bg-background/50"
            rows={1}
          />
        </div>

        {/* Line 3: Precedence */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 3: PRECEDENCE (Urgency Category)
          </Label>
          <Select
            value={fields.precedence}
            onValueChange={(v) => updateField("precedence", v)}
          >
            <SelectTrigger className="bg-background/50 border-border text-sm font-mono">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {precedenceOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  <div>
                    <div className="font-bold">{opt.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {opt.desc}
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Line 4: Special Equipment */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 4: SPECIAL EQUIPMENT REQUIRED
          </Label>
          <Select
            value={fields.special_equipment}
            onValueChange={(v) => updateField("special_equipment", v)}
          >
            <SelectTrigger className="bg-background/50 border-border text-sm font-mono">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {equipmentOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Line 5: Patients */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 5: NUMBER OF PATIENTS BY TYPE
          </Label>
          <Textarea
            value={fields.patients}
            onChange={(e) => updateField("patients", e.target.value)}
            placeholder="e.g., 2L (2 litter), 1A (1 ambulatory), format: #L = litter, #A = ambulatory"
            className="font-mono text-sm resize-none max-h-[100px] overflow-y-auto bg-background/50"
            rows={2}
          />
          <p className="text-[10px] text-muted-foreground">
            L = Litter (stretcher), A = Ambulatory (walking wounded)
          </p>
        </div>

        {/* Line 6: Security */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 6: SECURITY AT PICKUP SITE
          </Label>
          <Select
            value={fields.security}
            onValueChange={(v) => updateField("security", v)}
          >
            <SelectTrigger className="bg-background/50 border-border text-sm font-mono">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {securityOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Line 7: Marking Method */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 7: METHOD OF MARKING PICKUP SITE
          </Label>
          <Select
            value={fields.marking_method}
            onValueChange={(v) => updateField("marking_method", v)}
          >
            <SelectTrigger className="bg-background/50 border-border text-sm font-mono">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {markingOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Line 8: Nationality */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 8: PATIENT NATIONALITY/STATUS
          </Label>
          <Select
            value={fields.nationality}
            onValueChange={(v) => updateField("nationality", v)}
          >
            <SelectTrigger className="bg-background/50 border-border text-sm font-mono">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {nationalityOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Line 9: NBC Contamination */}
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground font-bold">
            LINE 9: NBC CONTAMINATION (Nuclear/Biological/Chemical)
          </Label>
          <Textarea
            value={fields.nbc_contamination}
            onChange={(e) => updateField("nbc_contamination", e.target.value)}
            placeholder="N = None, or specify: N (Nuclear), B (Biological), C (Chemical)"
            className="font-mono text-sm resize-none max-h-[100px] overflow-y-auto bg-background/50"
            rows={1}
          />
        </div>

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={loading || !fields.location || !fields.patients}
          className="w-full bg-red-600 hover:bg-red-700 text-white font-bold"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating CASEVAC...
            </>
          ) : (
            <>Generate 9-Line CASEVAC Request</>
          )}
        </Button>

        {/* Preview */}
        {generatedDoc && (
          <Card className="mt-4 p-4 bg-card/30 border-border">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-bold text-foreground">
                CASEVAC {casevacNumber?.toString().padStart(4, "0")} - PREVIEW
              </h3>
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
            <pre className="text-[10px] font-mono text-foreground/80 whitespace-pre-wrap bg-card/30 p-3 rounded border border-border">
              {generatedDoc}
            </pre>
          </Card>
        )}
      </div>
    </Card>
  );
}
