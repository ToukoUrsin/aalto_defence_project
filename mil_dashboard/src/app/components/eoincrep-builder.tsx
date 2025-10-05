"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Eye, Sparkles, Download, FileText } from "lucide-react";

interface EOINCREPBuilderProps {
  unitId: string;
  unitName: string;
  soldierIds: string[];
  reports: any[];
  suggestionId?: string | null;
}

interface EOINCREPFields {
  dtg: string;
  location: string;
  observer_id: string;
  enemy_type: string;
  enemy_count: string;
  vehicle_count: string;
  direction: string;
  equipment: string;
  activity: string;
  threat_level: string;
  recommended_action: string;
}

export function EOINCREPBuilder({
  unitId,
  unitName,
  soldierIds,
  reports,
  suggestionId,
}: EOINCREPBuilderProps) {
  const [fields, setFields] = useState<EOINCREPFields>({
    dtg: new Date().toISOString(),
    location: "",
    observer_id: "",
    enemy_type: "INFANTRY",
    enemy_count: "",
    vehicle_count: "0",
    direction: "N",
    equipment: "",
    activity: "",
    threat_level: "MEDIUM",
    recommended_action: "",
  });

  const [generatedDoc, setGeneratedDoc] = useState<string>("");
  const [eoincrepNumber, setEoincrepNumber] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [suggesting, setSuggesting] = useState(false);

  // Auto-generate DTG every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setFields((prev) => ({ ...prev, dtg: new Date().toISOString() }));
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const handleSuggest = async () => {
    setSuggesting(true);
    try {
      const response = await axios.post(
        "https://military-hierarchy-backend.onrender.com/eoincrep/suggest",
        {
          unit_id: unitId,
          unit_name: unitName,
          soldier_ids: soldierIds,
          reports: reports,
          suggestion_id: suggestionId,
        }
      );

      setFields((prev) => ({
        ...prev,
        ...response.data.suggested_fields,
      }));
    } catch (error: any) {
      console.error("Error getting AI suggestions:", error);
      const errorMsg =
        error.response?.data?.detail || error.message || "Unknown error";
      alert(`Failed to get AI suggestions: ${errorMsg}`);
    } finally {
      setSuggesting(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const sourceReportIds = reports
        .filter(
          (r) =>
            r.report_type === "CONTACT" ||
            r.report_type === "INTELLIGENCE" ||
            r.report_type === "SITREP"
        )
        .slice(0, 10)
        .map((r) => r.report_id);

      const response = await axios.post(
        "https://military-hierarchy-backend.onrender.com/eoincrep/generate",
        {
          unit_id: unitId,
          unit_name: unitName,
          eoincrep_fields: fields,
          source_report_ids: sourceReportIds,
        }
      );

      setGeneratedDoc(response.data.formatted_document);
      setEoincrepNumber(response.data.eoincrep_number);
    } catch (error: any) {
      console.error("Error generating EOINCREP:", error);
      const errorMsg =
        error.response?.data?.detail || error.message || "Unknown error";
      alert(`Failed to generate EOINCREP: ${errorMsg}`);
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
    a.download = `EOINCREP_${String(eoincrepNumber).padStart(
      4,
      "0"
    )}_${unitName.replace(/\s+/g, "_")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatDTG = (isoString: string) => {
    const date = new Date(isoString);
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hours = String(date.getUTCHours()).padStart(2, "0");
    const minutes = String(date.getUTCMinutes()).padStart(2, "0");
    const seconds = String(date.getUTCSeconds()).padStart(2, "0");
    const months = [
      "JAN",
      "FEB",
      "MAR",
      "APR",
      "MAY",
      "JUN",
      "JUL",
      "AUG",
      "SEP",
      "OCT",
      "NOV",
      "DEC",
    ];
    const month = months[date.getUTCMonth()];
    const year = date.getUTCFullYear();
    return `${day}${hours}${minutes}${seconds}Z ${month} ${year}`;
  };

  return (
    <Card className="h-full bg-card/50 backdrop-blur-sm border-border flex flex-col overflow-hidden">
      <div className="flex-shrink-0 p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-yellow-500" />
            <div>
              <h2 className="text-sm font-bold font-mono text-foreground tracking-wider">
                ENEMY OBSERVATION REPORT (EOINCREP)
              </h2>
              <p className="text-xs text-muted-foreground font-mono">
                {unitName}
              </p>
            </div>
          </div>
          <div className="flex gap-1">
            "
            <Button
              onClick={handleSuggest}
              disabled={suggesting || reports.length === 0}
              size="sm"
              variant="outline"
              className="h-7 text-xs border-yellow-500/50 hover:bg-yellow-500/10"
            >
              <Sparkles className="h-3 w-3 mr-1" />
              {suggesting ? "Analyzing..." : "AI Suggest"}
            </Button>
            <Button
              onClick={handleGenerate}
              disabled={loading || !fields.location}
              size="sm"
              className="h-7 text-xs bg-yellow-600 hover:bg-yellow-700 text-white"
            >
              <FileText className="h-3 w-3 mr-1" />
              {loading ? "Generating..." : "Generate EOINCREP"}
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0">
        {/* DTG (Auto-generated) */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            DTG (Date-Time Group) - Auto-Generated
          </Label>
          <Input
            value={formatDTG(fields.dtg)}
            disabled
            className="mt-1 font-mono text-xs bg-muted/50"
          />
        </div>

        {/* Location */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Location (Grid or Description) *
          </Label>
          <Input
            value={fields.location}
            onChange={(e) => setFields({ ...fields, location: e.target.value })}
            placeholder="Grid: NV123456 or terrain description"
            className="mt-1 font-mono text-xs bg-background/50"
          />
        </div>

        {/* Observer ID */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Observer ID/Info
          </Label>
          <Input
            value={fields.observer_id}
            onChange={(e) =>
              setFields({ ...fields, observer_id: e.target.value })
            }
            placeholder="Observer name, callsign, or unit"
            className="mt-1 font-mono text-xs bg-background/50"
          />
        </div>

        {/* Enemy Type */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Enemy Type
          </Label>
          <Select
            value={fields.enemy_type}
            onValueChange={(value) =>
              setFields({ ...fields, enemy_type: value })
            }
          >
            <SelectTrigger className="mt-1 font-mono text-xs bg-background/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="INFANTRY">Infantry</SelectItem>
              <SelectItem value="ARMOR">Armored Vehicles</SelectItem>
              <SelectItem value="ARTILLERY">Artillery</SelectItem>
              <SelectItem value="MIXED">Mixed Forces</SelectItem>
              <SelectItem value="UNKNOWN">Unknown</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {/* Enemy Count */}
          <div>
            <Label className="text-xs font-mono text-muted-foreground">
              Enemy Count (Personnel)
            </Label>
            <Input
              type="number"
              value={fields.enemy_count}
              onChange={(e) =>
                setFields({ ...fields, enemy_count: e.target.value })
              }
              placeholder="0"
              className="mt-1 font-mono text-xs bg-background/50"
            />
          </div>

          {/* Vehicle Count */}
          <div>
            <Label className="text-xs font-mono text-muted-foreground">
              Vehicle Count
            </Label>
            <Input
              type="number"
              value={fields.vehicle_count}
              onChange={(e) =>
                setFields({ ...fields, vehicle_count: e.target.value })
              }
              placeholder="0"
              className="mt-1 font-mono text-xs bg-background/50"
            />
          </div>
        </div>

        {/* Direction of Movement */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Direction of Movement
          </Label>
          <Select
            value={fields.direction}
            onValueChange={(value) =>
              setFields({ ...fields, direction: value })
            }
          >
            <SelectTrigger className="mt-1 font-mono text-xs bg-background/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="N">North (N)</SelectItem>
              <SelectItem value="NE">Northeast (NE)</SelectItem>
              <SelectItem value="E">East (E)</SelectItem>
              <SelectItem value="SE">Southeast (SE)</SelectItem>
              <SelectItem value="S">South (S)</SelectItem>
              <SelectItem value="SW">Southwest (SW)</SelectItem>
              <SelectItem value="W">West (W)</SelectItem>
              <SelectItem value="NW">Northwest (NW)</SelectItem>
              <SelectItem value="STATIONARY">Stationary</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Equipment Observed */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Equipment Observed
          </Label>
          <Textarea
            value={fields.equipment}
            onChange={(e) =>
              setFields({ ...fields, equipment: e.target.value })
            }
            placeholder="Describe weapons, vehicles, communication equipment..."
            rows={2}
            className="mt-1 font-mono text-xs bg-background/50 resize-none max-h-[100px] overflow-y-auto"
          />
        </div>

        {/* Activity/Behavior */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Activity/Behavior
          </Label>
          <Textarea
            value={fields.activity}
            onChange={(e) => setFields({ ...fields, activity: e.target.value })}
            placeholder="What are they doing? Patrolling, digging in, moving..."
            rows={2}
            className="mt-1 font-mono text-xs bg-background/50 resize-none max-h-[100px] overflow-y-auto"
          />
        </div>

        {/* Threat Level */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Threat Assessment
          </Label>
          <Select
            value={fields.threat_level}
            onValueChange={(value) =>
              setFields({ ...fields, threat_level: value })
            }
          >
            <SelectTrigger className="mt-1 font-mono text-xs bg-background/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="LOW">Low - Minimal threat</SelectItem>
              <SelectItem value="MEDIUM">Medium - Moderate concern</SelectItem>
              <SelectItem value="HIGH">High - Significant threat</SelectItem>
              <SelectItem value="CRITICAL">
                Critical - Immediate danger
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Recommended Action */}
        <div>
          <Label className="text-xs font-mono text-muted-foreground">
            Recommended Action
          </Label>
          <Textarea
            value={fields.recommended_action}
            onChange={(e) =>
              setFields({ ...fields, recommended_action: e.target.value })
            }
            placeholder="Suggest response: monitor, engage, call for support..."
            rows={2}
            className="mt-1 font-mono text-xs bg-background/50 resize-none max-h-[100px] overflow-y-auto"
          />
        </div>

        {/* Preview */}
        {generatedDoc && (
          <div className="border border-border rounded-md bg-card/30 p-3">
            <div className="flex items-center justify-between mb-2">
              <Label className="text-xs font-mono text-foreground">
                EOINCREP #{String(eoincrepNumber).padStart(4, "0")} - Preview
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
