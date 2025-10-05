"use client";

import React, { useState, useEffect } from "react";
import { AlertTriangle, Eye, X, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Suggestion {
  suggestion_id: string;
  suggestion_type: "CASEVAC" | "EOINCREP" | "EOINCREP_EOD";
  urgency: "URGENT" | "HIGH" | "MEDIUM" | "LOW";
  reason: string;
  confidence: number;
  source_reports: string[];
  status: string;
  created_at: string;
  unit_id: string;
}

interface AutoSuggestionsProps {
  unitId?: string;
  onCreateReport: (type: string, suggestionId: string, unitId: string) => void;
}

export function AutoSuggestions({
  unitId,
  onCreateReport,
}: AutoSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [lastCount, setLastCount] = useState(0);

  // Poll for suggestions every 5 seconds
  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const url = unitId
          ? `https://military-hierarchy-backend.onrender.com/api/suggestions?status=pending&unit_id=${unitId}`
          : "https://military-hierarchy-backend.onrender.com/api/suggestions?status=pending";

        const response = await fetch(url);
        const data = await response.json();

        setSuggestions(data.suggestions || []);

        // Show notification if new suggestions arrived
        if (data.suggestions.length > lastCount && lastCount > 0) {
          const newSuggestion = data.suggestions[0];
          showNotification(newSuggestion);
          setShowPanel(true); // Auto-open panel
        }

        setLastCount(data.suggestions.length);
      } catch (error) {
        console.error("Error fetching suggestions:", error);
      }
    };

    // Trigger reanalysis on first mount (when page loads)
    const reanalyzeReports = async () => {
      try {
        await fetch(
          "https://military-hierarchy-backend.onrender.com/api/suggestions/reanalyze",
          {
            method: "POST",
          }
        );
        console.log("✅ Reports reanalyzed for suggestions");
      } catch (error) {
        console.error("Error reanalyzing reports:", error);
      }
    };

    // Run reanalysis on mount
    reanalyzeReports();

    // Initial fetch
    fetchSuggestions();

    // Poll every 5 seconds
    const interval = setInterval(fetchSuggestions, 5000);

    return () => clearInterval(interval);
  }, [unitId]);

  const showNotification = (suggestion: Suggestion) => {
    // Play sound for URGENT
    if (suggestion.urgency === "URGENT") {
      playAlertSound();
    }

    // Show browser notification if permitted
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(getAlertTitle(suggestion), {
        body: suggestion.reason,
        tag: suggestion.suggestion_id,
      });
    }
  };

  const playAlertSound = () => {
    // Simple beep using Web Audio API
    try {
      const audioContext = new (window.AudioContext ||
        (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.value = 800;
      oscillator.type = "sine";
      gainNode.gain.value = 0.3;

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
      console.error("Error playing sound:", e);
    }
  };

  const dismissSuggestion = async (suggestionId: string) => {
    try {
      await fetch(
        `https://military-hierarchy-backend.onrender.com/api/suggestions/${suggestionId}`,
        {
          method: "DELETE",
        }
      );

      setSuggestions((prev) =>
        prev.filter((s) => s.suggestion_id !== suggestionId)
      );
    } catch (error) {
      console.error("Error dismissing suggestion:", error);
    }
  };

  const handleCreateReport = async (suggestion: Suggestion) => {
    try {
      // Mark as draft_created
      await fetch(
        `https://military-hierarchy-backend.onrender.com/api/suggestions/${suggestion.suggestion_id}/create-draft`,
        {
          method: "POST",
        }
      );

      // Trigger report builder and select the unit
      onCreateReport(
        suggestion.suggestion_type,
        suggestion.suggestion_id,
        suggestion.unit_id
      );

      // Remove from list
      setSuggestions((prev) =>
        prev.filter((s) => s.suggestion_id !== suggestion.suggestion_id)
      );
    } catch (error) {
      console.error("Error creating report:", error);
    }
  };

  const getAlertTitle = (suggestion: Suggestion): string => {
    const emoji = {
      CASEVAC: "⚠️",
      EOINCREP: "👁️",
      EOINCREP_EOD: "💣",
    }[suggestion.suggestion_type];

    return `${emoji} ${suggestion.suggestion_type} RECOMMENDED`;
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "CASEVAC":
        return <AlertTriangle className="h-4 w-4" />;
      case "EOINCREP":
      case "EOINCREP_EOD":
        return <Eye className="h-4 w-4" />;
      default:
        return <Bell className="h-4 w-4" />;
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "URGENT":
        return "bg-black border-red-500";
      case "HIGH":
        return "bg-black border-orange-500";
      case "MEDIUM":
        return "bg-black border-yellow-500";
      default:
        return "bg-black border-border";
    }
  };

  const getUrgencyIconColor = (urgency: string) => {
    switch (urgency) {
      case "URGENT":
        return "text-red-500";
      case "HIGH":
        return "text-orange-500";
      case "MEDIUM":
        return "text-yellow-500";
      default:
        return "text-muted-foreground";
    }
  };

  return (
    <DropdownMenu open={showPanel} onOpenChange={setShowPanel}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="relative h-8 w-8 p-0"
          title={`${suggestions.length} AI suggestions`}
        >
          <Bell className="h-4 w-4 text-white" />
          {suggestions.length > 0 && (
            <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center font-bold animate-pulse">
              {suggestions.length}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-96 max-h-[500px] overflow-y-auto bg-black text-foreground border-border shadow-lg"
      >
        <div className="sticky top-0 bg-black border-b border-border p-3 z-10">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">
              🤖 AI Suggestions ({suggestions.length})
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowPanel(false)}
              className="h-6 w-6 p-0"
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>

        <div className="p-3 space-y-3">
          {suggestions.length === 0 ? (
            <div className="text-center py-8 text-white">
              <Bell className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No pending suggestions</p>
              <p className="text-xs mt-1">
                AI will analyze reports as they arrive
              </p>
            </div>
          ) : (
            suggestions.map((suggestion) => {
              const iconColor = getUrgencyIconColor(suggestion.urgency);
              return (
                <Card
                  key={suggestion.suggestion_id}
                  className={`p-3 bg-black text-white border ${getUrgencyColor(
                    suggestion.urgency
                  )}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={iconColor}>
                        {getAlertIcon(suggestion.suggestion_type)}
                      </span>
                      <span className="text-xs font-bold text-white">
                        {suggestion.suggestion_type.replace("_", " ")}
                      </span>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded bg-muted font-semibold text-muted-foreground">
                      {suggestion.urgency}
                    </span>
                  </div>

                  <p className="text-xs mb-3 leading-relaxed text-white/80">
                    {suggestion.reason}
                  </p>

                  <div className="flex items-center justify-between mb-3 text-xs text-white/60">
                    <span>
                      Confidence: {Math.round(suggestion.confidence * 100)}%
                    </span>
                    <span>
                      {suggestion.source_reports.length} source report
                      {suggestion.source_reports.length !== 1 ? "s" : ""}
                    </span>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleCreateReport(suggestion)}
                      className={`flex-1 h-8 text-xs font-semibold ${
                        suggestion.urgency === "URGENT"
                          ? "bg-red-600 hover:bg-red-700 text-white"
                          : "bg-primary hover:bg-primary/90"
                      }`}
                    >
                      Create {suggestion.suggestion_type.split("_")[0]}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        dismissSuggestion(suggestion.suggestion_id)
                      }
                      className="h-8 px-3 text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function getAlertTitle(suggestion: Suggestion): string {
  const emoji = {
    CASEVAC: "⚠️",
    EOINCREP: "👁️",
    EOINCREP_EOD: "💣",
  }[suggestion.suggestion_type];

  return `${emoji} ${suggestion.suggestion_type} RECOMMENDED`;
}
