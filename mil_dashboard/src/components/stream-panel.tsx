"use client";

import type React from "react";

import { useState, useEffect } from "react";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Send,
  Radio,
  AlertTriangle,
  Shield,
  Activity,
  Zap,
  Eye,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface StreamPanelProps {
  streamId: string;
  onItemClick: (item: any) => void;
}

type ReportType =
  | "EOINCREP"
  | "CASEVAC"
  | "SITREP"
  | "MEDEVAC"
  | "SPOTREP"
  | "INTREP";

interface BattlefieldReport {
  id: number;
  type: ReportType;
  text: string;
  timestamp: Date;
  unit: string;
  coordinates?: string;
  priority?: "ROUTINE" | "PRIORITY" | "IMMEDIATE" | "FLASH";
  casualties?: number;
}

export function StreamPanel({ streamId, onItemClick }: StreamPanelProps) {
  const [message, setMessage] = useState("");
  const [updates, setUpdates] = useState<BattlefieldReport[]>([]);
  const [loading, setLoading] = useState(false);
  const API_BASE = "https://military-hierarchy-backend.onrender.com/";

  // Fetch existing reports on mount and periodically
  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchReports = async () => {
    try {
      const response = await axios.get(`${API_BASE}/reports?limit=50`);
      const reports = response.data.reports || [];

      // Transform backend reports to BattlefieldReport format
      const transformedReports: BattlefieldReport[] = reports.map(
        (report: any, index: number) => {
          const structuredData =
            typeof report.structured_json === "string"
              ? JSON.parse(report.structured_json)
              : report.structured_json;

          // Handle casualties - can be a number or array of casualty objects
          let casualtyCount: number | undefined;
          if (structuredData.casualties) {
            if (Array.isArray(structuredData.casualties)) {
              casualtyCount = structuredData.casualties.length;
            } else if (typeof structuredData.casualties === "number") {
              casualtyCount = structuredData.casualties;
            }
          }

          return {
            id: index + 1,
            type: report.report_type as ReportType,
            text:
              structuredData.description ||
              structuredData.status ||
              structuredData.observation ||
              JSON.stringify(structuredData),
            timestamp: new Date(report.timestamp),
            unit: report.soldier_name || report.unit_name || "Unknown Unit",
            coordinates: structuredData.location || structuredData.coordinates,
            priority: structuredData.priority as any,
            casualties: casualtyCount,
          };
        }
      );

      setUpdates(transformedReports);
    } catch (error) {
      console.error("Error fetching reports:", error);
    }
  };

  const handleSend = async () => {
    if (!message.trim() || loading) return;

    setLoading(true);
    try {
      // Submit to backend API - using ALPHA_01 as default soldier
      const reportData = {
        report_type: "SITREP",
        structured_json: {
          status: message,
          location: "Unknown",
          timestamp: new Date().toISOString(),
        },
        confidence: 0.95,
      };

      await axios.post(`${API_BASE}/soldiers/ALPHA_01/reports`, reportData);

      setMessage("");
      // Refresh reports to show the new one
      fetchReports();
    } catch (error) {
      console.error("Error submitting report:", error);
      alert("Failed to submit report. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getReportTypeColor = (type: ReportType) => {
    return "text-foreground/70";
  };

  const getReportTypeBg = (type: ReportType) => {
    switch (type) {
      case "CASEVAC":
      case "MEDEVAC":
        return "bg-military-red/20 border-military-red/30";
      case "EOINCREP":
      case "SPOTREP":
        return "bg-military-amber/20 border-military-amber/30";
      case "INTREP":
        return "bg-military-blue/20 border-military-blue/30";
      case "SITREP":
        return "bg-military-olive/20 border-military-olive/30";
      default:
        return "bg-foreground/10";
    }
  };

  const getReportIcon = (type: ReportType) => {
    switch (type) {
      case "CASEVAC":
      case "MEDEVAC":
        return AlertTriangle;
      case "EOINCREP":
        return Eye;
      case "SPOTREP":
        return Zap;
      case "INTREP":
        return Activity;
      case "SITREP":
        return Shield;
      default:
        return Radio;
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case "FLASH":
      case "IMMEDIATE":
        return "bg-military-red text-white";
      case "PRIORITY":
        return "bg-military-amber text-black";
      default:
        return "bg-foreground/30 text-foreground";
    }
  };

  return (
    <Card className="neumorphic border-0 overflow-hidden">
      <div className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold font-mono flex items-center gap-2 text-foreground">
            <Radio className="h-5 w-5" />
            BATTLEFIELD REPORTS
          </h2>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-foreground/50 animate-pulse" />
            <span className="text-xs text-muted-foreground font-mono">
              LIVE
            </span>
          </div>
        </div>

        {/* Input Field */}
        <div className="relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Submit report..."
            className="neumorphic-inset border-0 pr-12 font-mono text-sm focus-visible:ring-foreground/50 focus-visible:ring-2"
          />
          <Button
            size="icon"
            onClick={handleSend}
            className="absolute right-1 top-1 h-8 w-8 bg-foreground/10 text-foreground hover:bg-foreground/20 transition-all duration-300"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Updates Stream */}
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
          {updates.map((update) => {
            const ReportIcon = getReportIcon(update.type);
            return (
              <div
                key={update.id}
                onClick={() => onItemClick(update)}
                className={cn(
                  "p-4 rounded-lg cursor-pointer transition-all duration-300 hover:scale-[1.02]",
                  "neumorphic-inset border",
                  getReportTypeBg(update.type),
                  "hover:shadow-lg"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-xs font-bold font-mono flex items-center gap-1 text-foreground",
                          getReportTypeBg(update.type)
                        )}
                      >
                        <ReportIcon className="h-3 w-3" />
                        {update.type}
                      </span>
                      {update.priority && (
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded text-xs font-bold font-mono",
                            getPriorityColor(update.priority)
                          )}
                        >
                          {update.priority}
                        </span>
                      )}
                      {update.casualties && (
                        <span className="px-2 py-0.5 rounded text-xs font-bold font-mono bg-military-red/30 text-foreground flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          {update.casualties}x
                        </span>
                      )}
                    </div>

                    <p className="text-sm font-medium leading-relaxed text-foreground">
                      {update.text}
                    </p>

                    <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                      <span>{update.unit}</span>
                      {update.coordinates && (
                        <>
                          <span>•</span>
                          <span>{update.coordinates}</span>
                        </>
                      )}
                      <span>•</span>
                      <span>{update.timestamp.toLocaleTimeString()}</span>
                    </div>
                  </div>
                  <div
                    className={cn("h-2 w-2 rounded-full mt-2 bg-foreground/50")}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
