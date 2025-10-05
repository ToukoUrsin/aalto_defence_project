"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  Shield,
  Building2,
  User,
  Radio,
  Clock,
  Activity,
  FileText,
  MapPin,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface Unit {
  unit_id: string;
  name: string;
  parent_unit_id: string | null;
  level: string;
  created_at: string;
}

interface Soldier {
  soldier_id: string;
  name: string;
  rank: string;
  unit_id: string;
  device_id: string;
  status: string;
  created_at: string;
  last_seen: string;
}

interface RawInput {
  input_id: string;
  soldier_id: string;
  timestamp: string;
  raw_text: string;
  raw_audio_ref?: string;
  input_type: string;
  confidence: number;
  location_ref?: string;
  created_at: string;
}

interface Report {
  report_id: string;
  soldier_id: string;
  unit_id: string;
  timestamp: string;
  report_type: string;
  structured_json: string;
  confidence: number;
  source_input_id?: string;
  status: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
  soldier_name?: string;
  unit_name?: string;
}

type SelectedNode = (Unit & { soldiers?: Soldier[] }) | Soldier;

interface DetailPanelProps {
  selectedNode: SelectedNode | null;
}

export function DetailPanel({ selectedNode }: DetailPanelProps) {
  const [rawInputs, setRawInputs] = useState<RawInput[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "inputs" | "reports">(
    "overview"
  );

  useEffect(() => {
    if (selectedNode) {
      fetchNodeData();
    }
  }, [selectedNode]);

  const fetchNodeData = async () => {
    if (!selectedNode) return;

    setLoading(true);
    try {
      // Check if it's a soldier (has soldier_id) or a unit
      if ("soldier_id" in selectedNode) {
        // Fetch soldier-specific data
        const [inputsResponse, reportsResponse] = await Promise.all([
          fetch(
            `https://military-hierarchy-backend.onrender.com//soldiers/${selectedNode.soldier_id}/raw_inputs`
          ),
          fetch(
            `https://military-hierarchy-backend.onrender.com//soldiers/${selectedNode.soldier_id}/reports`
          ),
        ]);

        const inputsData = await inputsResponse.json();
        const reportsData = await reportsResponse.json();

        setRawInputs(inputsData.raw_inputs || []);
        setReports(reportsData.reports || []);
      } else {
        // For units, fetch all reports from soldiers in that unit
        const response = await fetch(
          `https://military-hierarchy-backend.onrender.com//units/${selectedNode.unit_id}/soldiers`
        );
        const soldiersData = await response.json();

        if (soldiersData.soldiers && soldiersData.soldiers.length > 0) {
          // Fetch reports for all soldiers in the unit
          const reportPromises = soldiersData.soldiers.map((soldier: any) =>
            fetch(
              `https://military-hierarchy-backend.onrender.com//soldiers/${soldier.soldier_id}/reports`
            )
          );

          const reportResponses = await Promise.all(reportPromises);
          const allReports = [];

          for (const res of reportResponses) {
            const data = await res.json();
            allReports.push(...(data.reports || []));
          }

          setReports(allReports);
          setRawInputs([]); // Units don't have direct raw inputs
        }
      }
    } catch (error) {
      console.error("Error fetching node data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeIcon = (node: SelectedNode) => {
    if ("soldier_id" in node) {
      return <User className="h-5 w-5 text-blue-500" />;
    } else {
      switch (node.level.toLowerCase()) {
        case "battalion":
          return <Building2 className="h-5 w-5 text-blue-500" />;
        case "company":
          return <Shield className="h-5 w-5 text-green-500" />;
        case "platoon":
          return <Users className="h-5 w-5 text-orange-500" />;
        case "squad":
          return <User className="h-5 w-5 text-purple-500" />;
        default:
          return <Users className="h-5 w-5 text-gray-500" />;
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "injured":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "missing":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getReportTypeColor = (type: string) => {
    switch (type) {
      case "CASEVAC":
      case "MEDEVAC":
        return "bg-military-red/20 text-foreground border-military-red/30";
      case "EOINCREP":
      case "SPOTREP":
        return "bg-military-amber/20 text-foreground border-military-amber/30";
      case "INTREP":
        return "bg-military-blue/20 text-foreground border-military-blue/30";
      case "SITREP":
        return "bg-military-olive/20 text-foreground border-military-olive/30";
      default:
        return "bg-muted text-foreground border-border";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!selectedNode) {
    return (
      <div className="h-full flex items-center justify-center bg-card">
        <div className="text-center text-muted-foreground">
          <Users className="h-12 w-12 mx-auto mb-2 text-muted-foreground/50" />
          <p className="font-mono">Select a unit or soldier to view details</p>
        </div>
      </div>
    );
  }

  const isSoldier = "soldier_id" in selectedNode;

  return (
    <div className="h-full flex flex-col bg-card">
      {/* Header */}
      <div className="p-6 border-b border-border bg-card/50">
        <div className="flex items-center gap-3">
          {getNodeIcon(selectedNode)}
          <div>
            <h2 className="text-xl font-bold font-mono text-foreground">
              {selectedNode.name}
            </h2>
            <p className="text-sm text-muted-foreground font-mono">
              {isSoldier ? selectedNode.rank : selectedNode.level}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        <button
          className={`px-4 py-3 text-sm font-medium font-mono transition-colors ${
            activeTab === "overview"
              ? "text-foreground border-b-2 border-foreground bg-muted/50"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
          }`}
          onClick={() => setActiveTab("overview")}
        >
          OVERVIEW
        </button>
        <button
          className={`px-4 py-3 text-sm font-medium font-mono transition-colors ${
            activeTab === "inputs"
              ? "text-foreground border-b-2 border-foreground bg-muted/50"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
          }`}
          onClick={() => setActiveTab("inputs")}
        >
          RAW INPUTS ({rawInputs.length})
        </button>
        <button
          className={`px-4 py-3 text-sm font-medium font-mono transition-colors ${
            activeTab === "reports"
              ? "text-foreground border-b-2 border-foreground bg-muted/50"
              : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
          }`}
          onClick={() => setActiveTab("reports")}
        >
          REPORTS ({reports.length})
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="p-4">
            {activeTab === "overview" && (
              <div className="space-y-4">
                {/* Basic Info */}
                <div className="neumorphic-inset rounded-lg p-6 border border-border/30">
                  <h3 className="font-medium text-foreground mb-4 font-mono">
                    BASIC INFORMATION
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground font-mono">
                        ID:
                      </span>
                      <span className="font-mono text-foreground">
                        {isSoldier
                          ? selectedNode.soldier_id
                          : selectedNode.unit_id}
                      </span>
                    </div>
                    {isSoldier && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground font-mono">
                            Device:
                          </span>
                          <span className="font-mono text-foreground">
                            {selectedNode.device_id}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground font-mono">
                            Status:
                          </span>
                          <div className="flex items-center gap-1">
                            {getStatusIcon(selectedNode.status)}
                            <span className="capitalize text-foreground font-mono">
                              {selectedNode.status}
                            </span>
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground font-mono">
                            Last Seen:
                          </span>
                          <span className="font-mono text-foreground">
                            {formatTimestamp(selectedNode.last_seen)}
                          </span>
                        </div>
                      </>
                    )}
                    <div className="flex justify-between">
                      <span className="text-muted-foreground font-mono">
                        Created:
                      </span>
                      <span className="font-mono text-foreground">
                        {formatTimestamp(selectedNode.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="neumorphic-inset rounded-lg p-4 border border-border/30">
                    <div className="flex items-center gap-2 mb-1">
                      <FileText className="h-4 w-4 text-foreground" />
                      <span className="text-sm font-medium text-foreground font-mono">
                        REPORTS
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-foreground font-mono">
                      {reports.length}
                    </div>
                  </div>

                  {isSoldier && (
                    <div className="neumorphic-inset rounded-lg p-4 border border-border/30">
                      <div className="flex items-center gap-2 mb-1">
                        <Radio className="h-4 w-4 text-foreground" />
                        <span className="text-sm font-medium text-foreground font-mono">
                          INPUTS
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-foreground font-mono">
                        {rawInputs.length}
                      </div>
                    </div>
                  )}
                </div>

                {/* Recent Activity */}
                {reports.length > 0 && (
                  <div className="neumorphic-inset rounded-lg p-6 border border-border/30">
                    <h3 className="font-medium text-foreground mb-4 font-mono">
                      RECENT ACTIVITY
                    </h3>
                    <div className="space-y-3">
                      {reports.slice(0, 3).map((report) => (
                        <div
                          key={report.report_id}
                          className="flex items-center gap-3 p-3 bg-card rounded border border-border/20"
                        >
                          <span
                            className={`px-2 py-1 text-xs rounded border font-mono ${getReportTypeColor(
                              report.report_type
                            )}`}
                          >
                            {report.report_type}
                          </span>
                          <span className="text-sm text-foreground flex-1 truncate font-mono">
                            {report.soldier_name || "Unknown"}
                          </span>
                          <span className="text-xs text-muted-foreground font-mono">
                            {formatTimestamp(report.timestamp)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "inputs" && (
              <div className="space-y-3">
                {rawInputs.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Radio className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                    <p>No raw inputs available</p>
                  </div>
                ) : (
                  rawInputs.map((input) => (
                    <div key={input.input_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {input.input_type.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(input.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 mb-2">
                        {input.raw_text}
                      </p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>
                          Confidence: {(input.confidence * 100).toFixed(0)}%
                        </span>
                        {input.location_ref && (
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {input.location_ref}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === "reports" && (
              <div className="space-y-3">
                {reports.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                    <p>No reports available</p>
                  </div>
                ) : (
                  reports.map((report) => (
                    <div
                      key={report.report_id}
                      className="border rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`px-2 py-1 text-xs rounded border font-medium ${getReportTypeColor(
                            report.report_type
                          )}`}
                        >
                          {report.report_type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(report.timestamp)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Soldier:</span>{" "}
                        {report.soldier_name}
                      </div>
                      <div className="text-sm text-gray-600 mb-3">
                        <span className="font-medium">Confidence:</span>{" "}
                        {(report.confidence * 100).toFixed(0)}%
                      </div>
                      <div className="bg-gray-50 rounded p-3">
                        <pre className="text-xs text-gray-800 whitespace-pre-wrap">
                          {JSON.stringify(
                            JSON.parse(report.structured_json),
                            null,
                            2
                          )}
                        </pre>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
