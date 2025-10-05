"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { HierarchyTree, type TreeNode } from "@/components/hierarchy-tree";
import { AIChat } from "@/components/ai-chat";
import { NodeReports } from "@/components/node-reports";
import { StreamPanel } from "@/components/stream-panel";
import { DataStreamSelector } from "@/components/data-stream-selector";
import { ReportDrawer } from "@/components/report-drawer";
import { SummaryModal } from "@/components/summary-modal";
import { FRAGOBuilder } from "./components/frago-builder";
import { CASEVACBuilder } from "./components/casevac-builder";
import { EOINCREPBuilder } from "./components/eoincrep-builder";
import { AutoSuggestions } from "@/components/auto-suggestions";
import {
  Shield,
  Users,
  Layers,
  FileBarChart,
  Radio,
  FileText,
  AlertTriangle,
  Eye,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface Soldier {
  soldier_id: string;
  name: string;
  rank: string;
  unit_id: string;
  device_id: string;
  unit_name: string;
  unit_level: string;
}

interface RawInput {
  input_id: string;
  soldier_id: string;
  timestamp: string;
  raw_text: string;
  raw_audio_ref?: string;
}

interface Report {
  report_id: string;
  soldier_id: string;
  unit_id: string;
  timestamp: string;
  report_type: string;
  structured_json: string;
  confidence: number;
  soldier_name: string;
  unit_name: string;
}

export default function Home() {
  const [soldiers, setSoldiers] = useState<Soldier[]>([]);
  const [selectedSoldier, setSelectedSoldier] = useState<string>("");
  const [rawInputs, setRawInputs] = useState<RawInput[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUnit, setSelectedUnit] = useState("battalion");
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [showFRAGOBuilder, setShowFRAGOBuilder] = useState(false);
  const [showCASEVACBuilder, setShowCASEVACBuilder] = useState(false);
  const [showEOINCREPBuilder, setShowEOINCREPBuilder] = useState(false);
  const [showReports, setShowReports] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [activeReportType, setActiveReportType] = useState<
    "FRAGO" | "CASEVAC" | "EOINCREP"
  >("FRAGO");
  const [activeSuggestionId, setActiveSuggestionId] = useState<string | null>(
    null
  );

  // New state for hierarchy tree and node selection
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [nodeReports, setNodeReports] = useState<Report[]>([]);
  const [loadingNodeReports, setLoadingNodeReports] = useState(false);

  const API_BASE = "https://military-hierarchy-backend.onrender.com";

  const unitLevels = [
    { id: "brigade", name: "Brigade", icon: Layers },
    { id: "battalion", name: "Battalion", icon: Shield },
    { id: "company", name: "Company", icon: Users },
    { id: "platoon", name: "Platoon", icon: Users },
    { id: "squad", name: "Squad", icon: Users },
  ];

  useEffect(() => {
    fetchSoldiers();
  }, []);

  useEffect(() => {
    if (selectedSoldier) {
      fetchSoldierData(selectedSoldier);
    }
  }, [selectedSoldier]);

  const fetchSoldiers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/soldiers`);
      setSoldiers(response.data.soldiers);
      if (response.data.soldiers.length > 0) {
        setSelectedSoldier(response.data.soldiers[0].soldier_id);
      }
    } catch (error) {
      console.error("Error fetching soldiers:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSoldierData = async (soldierId: string) => {
    try {
      const [rawResponse, reportsResponse] = await Promise.all([
        axios.get(`${API_BASE}/soldiers/${soldierId}/raw_inputs`),
        axios.get(`${API_BASE}/soldiers/${soldierId}/reports`),
      ]);

      setRawInputs(rawResponse.data.raw_inputs);
      setReports(reportsResponse.data.reports);
    } catch (error) {
      console.error("Error fetching soldier data:", error);
    }
  };

  // Helper function to recursively collect all soldier IDs from a unit and its subunits
  const collectSoldierIds = (node: TreeNode): string[] => {
    let soldierIds: string[] = [];

    // Add soldiers directly in this unit
    if (node.soldiers) {
      soldierIds.push(...node.soldiers.map((s: any) => s.soldier_id));
    }

    // Recursively add soldiers from subunits
    if (node.subunits) {
      for (const subunit of node.subunits) {
        // Convert Unit to TreeNode-like structure for recursion
        const subunitNode: TreeNode = {
          id: subunit.unit_id,
          name: subunit.name,
          type: "unit",
          unit_id: subunit.unit_id,
          soldiers: subunit.soldiers,
          subunits: subunit.subunits,
        };
        soldierIds.push(...collectSoldierIds(subunitNode));
      }
    }

    return soldierIds;
  };

  // Fetch reports for selected node (soldier or unit with subordinates)
  const fetchNodeReports = async (node: TreeNode) => {
    setLoadingNodeReports(true);
    try {
      let allReports: Report[] = [];

      if (node.type === "soldier") {
        // Fetch reports for single soldier
        const response = await axios.get(
          `${API_BASE}/soldiers/${node.soldier_id}/reports`
        );
        allReports = response.data.reports || [];
      } else if (node.type === "unit") {
        // Collect all soldier IDs from this unit and its subordinate units
        const soldierIds = collectSoldierIds(node);

        // Fetch all reports and filter by soldier IDs
        const response = await axios.get(`${API_BASE}/reports?limit=500`);
        const allAvailableReports = response.data.reports || [];

        // Filter reports that belong to soldiers in this unit hierarchy
        allReports = allAvailableReports.filter((report: Report) =>
          soldierIds.includes(report.soldier_id)
        );
      }

      setNodeReports(allReports);
    } catch (error) {
      console.error("Error fetching node reports:", error);
      setNodeReports([]);
    } finally {
      setLoadingNodeReports(false);
    }
  };

  // Handle node selection from hierarchy tree
  const handleNodeSelect = (node: TreeNode) => {
    setSelectedNode(node);
    fetchNodeReports(node);
  };

  // Select a unit by its unit_id (for suggestion navigation)
  const selectUnitById = async (unitId: string) => {
    try {
      // Fetch hierarchy to find the node
      const response = await axios.get(`${API_BASE}/hierarchy`);
      const hierarchy = response.data.hierarchy || [];

      // Recursively search for the unit node
      const findNode = (nodes: any[]): TreeNode | null => {
        for (const node of nodes) {
          // Check if this is the unit we're looking for
          if (node.unit_id === unitId) {
            // Convert to TreeNode format
            return {
              id: node.unit_id,
              name: node.name,
              type: "unit" as const,
              level: node.level,
              unit_id: node.unit_id,
              children: node.subunits || [],
              soldiers: node.soldiers || [],
              subunits: node.subunits || [],
            };
          }

          // Check subunits
          if (node.subunits && node.subunits.length > 0) {
            const found = findNode(node.subunits);
            if (found) return found;
          }
        }
        return null;
      };

      const foundNode = findNode(hierarchy);
      if (foundNode) {
        handleNodeSelect(foundNode);
      } else {
        console.warn(`Unit with id ${unitId} not found in hierarchy`);
      }
    } catch (error) {
      console.error("Error selecting unit by ID:", error);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getReportTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      CASEVAC: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
      EOINCREP:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
      SITREP:
        "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
      FRAGO:
        "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
      OPORD:
        "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
    };
    return (
      colors[type] ||
      "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300"
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-xl text-foreground">
          Loading military dashboard...
        </div>
      </div>
    );
  }

  return (
    <div className="dark min-h-screen bg-background grid-background">
      <div className="flex h-screen">
        {/* Left Sidebar Navigation */}
        <div
          className={`${
            sidebarExpanded ? "w-52" : "w-16"
          } bg-card backdrop-blur-sm border-r border-border flex flex-col py-6 gap-1 flex-shrink-0 transition-all duration-300`}
        >
          {/* Expand/Collapse Toggle */}
          <div className="px-3 mb-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setSidebarExpanded(!sidebarExpanded)}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 text-muted-foreground hover:text-foreground hover:bg-muted/50`}
            >
              <Layers className="h-4 w-4" />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  MENU
                </span>
              )}
            </Button>
          </div>

          <div className="h-px bg-border/30 mx-3 mb-2" />

          {/* Reports Button */}
          <div className="px-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowReports(true);
                setShowChat(false);
                setShowFRAGOBuilder(false);
                setShowCASEVACBuilder(false);
                setShowEOINCREPBuilder(false);
              }}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 hover:bg-muted/50 ${
                showReports
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground"
              }`}
              title="Reports"
            >
              <FileText
                className={`h-4 w-4 ${showReports ? "text-blue-500" : ""}`}
              />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  REPORTS
                </span>
              )}
            </Button>
          </div>

          {/* AI Chat Button */}
          <div className="px-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowReports(false);
                setShowChat(true);
                setShowFRAGOBuilder(false);
                setShowCASEVACBuilder(false);
                setShowEOINCREPBuilder(false);
              }}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 hover:bg-muted/50 ${
                showChat ? "bg-muted text-foreground" : "text-muted-foreground"
              }`}
              title="AI Chat"
            >
              <Radio
                className={`h-4 w-4 ${showChat ? "text-purple-500" : ""}`}
              />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  AI CHAT
                </span>
              )}
            </Button>
          </div>

          <div className="h-px bg-border/30 mx-3 my-2" />

          {/* FRAGO Button */}
          <div className="px-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowReports(false);
                setShowChat(false);
                setShowFRAGOBuilder(true);
                setShowCASEVACBuilder(false);
                setShowEOINCREPBuilder(false);
                setActiveReportType("FRAGO");
              }}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 hover:bg-muted/50 ${
                showFRAGOBuilder
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground"
              }`}
              title="FRAGO"
            >
              <FileText
                className={`h-4 w-4 ${
                  showFRAGOBuilder ? "text-green-500" : ""
                }`}
              />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  FRAGO
                </span>
              )}
            </Button>
          </div>

          {/* CASEVAC Button */}
          <div className="px-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowReports(false);
                setShowChat(false);
                setShowFRAGOBuilder(false);
                setShowCASEVACBuilder(true);
                setShowEOINCREPBuilder(false);
                setActiveReportType("CASEVAC");
              }}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 hover:bg-muted/50 ${
                showCASEVACBuilder
                  ? "bg-muted text-foreground border-l-2 border-red-500"
                  : "text-muted-foreground"
              }`}
              title="CASEVAC"
            >
              <AlertTriangle
                className={`h-4 w-4 ${
                  showCASEVACBuilder ? "text-red-500" : ""
                }`}
              />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  CASEVAC
                </span>
              )}
            </Button>
          </div>

          {/* EOINCREP Button */}
          <div className="px-3">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowReports(false);
                setShowChat(false);
                setShowFRAGOBuilder(false);
                setShowCASEVACBuilder(false);
                setShowEOINCREPBuilder(true);
                setActiveReportType("EOINCREP");
              }}
              className={`${
                sidebarExpanded ? "w-full justify-start" : "w-10 justify-center"
              } h-10 hover:bg-muted/50 ${
                showEOINCREPBuilder
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground"
              }`}
              title="EOINCREP"
            >
              <Eye
                className={`h-4 w-4 ${
                  showEOINCREPBuilder ? "text-yellow-500" : ""
                }`}
              />
              {sidebarExpanded && (
                <span className="ml-3 text-xs font-mono tracking-wider">
                  EOINCREP
                </span>
              )}
            </Button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="flex items-center justify-between bg-card/50 backdrop-blur-sm p-3 border-b border-border flex-shrink-0">
            <div>
              <h1 className="text-2xl font-bold tracking-tight font-mono text-foreground">
                TACTICAL OPS DASHBOARD
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Real-time battlefield reporting and soldier monitoring
              </p>
            </div>

            <div className="flex items-center gap-2">
              <AutoSuggestions
                unitId={selectedNode?.unit_id || selectedNode?.id}
                onCreateReport={(type, suggestionId, unitId) => {
                  setActiveReportType(type as "FRAGO" | "CASEVAC" | "EOINCREP");
                  setActiveSuggestionId(suggestionId);

                  // Select the unit associated with the suggestion
                  selectUnitById(unitId);

                  if (type === "FRAGO") {
                    setShowReports(false);
                    setShowChat(false);
                    setShowFRAGOBuilder(true);
                    setShowCASEVACBuilder(false);
                    setShowEOINCREPBuilder(false);
                  } else if (type === "CASEVAC") {
                    setShowReports(false);
                    setShowChat(false);
                    setShowCASEVACBuilder(true);
                    setShowFRAGOBuilder(false);
                    setShowEOINCREPBuilder(false);
                  } else if (type === "EOINCREP" || type === "EOINCREP_EOD") {
                    setShowReports(false);
                    setShowChat(false);
                    setShowEOINCREPBuilder(true);
                    setShowFRAGOBuilder(false);
                    setShowCASEVACBuilder(false);
                  }
                }}
              />
              <Button
                onClick={() => setShowSummaryModal(true)}
                className="bg-foreground/10 hover:bg-foreground/20 text-foreground font-mono border border-border h-8 text-xs"
                size="sm"
              >
                <FileBarChart className="h-3 w-3 mr-1" />
                SUMMARY
              </Button>
            </div>
          </header>

          {/* Main Content Grid */}
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 overflow-hidden">
            {/* Left: Hierarchy Tree */}
            <div className="lg:col-span-1 h-full">
              <HierarchyTree
                onNodeSelect={handleNodeSelect}
                selectedNodeId={selectedNode?.id}
              />
            </div>

            {/* Right: Content based on active view */}
            <div className="lg:col-span-3 h-full overflow-hidden">
              {showReports && (
                <NodeReports
                  selectedNode={selectedNode}
                  reports={nodeReports}
                  loading={loadingNodeReports}
                  onReportClick={setSelectedItem}
                />
              )}

              {showChat && (
                <AIChat selectedNode={selectedNode} reports={nodeReports} />
              )}

              {showFRAGOBuilder && selectedNode && (
                <FRAGOBuilder
                  unitId={selectedNode.unit_id || selectedNode.id}
                  unitName={selectedNode.name}
                  soldierIds={collectSoldierIds(selectedNode)}
                  reports={nodeReports}
                  suggestionId={activeSuggestionId}
                />
              )}

              {showCASEVACBuilder && selectedNode && (
                <CASEVACBuilder
                  unitId={selectedNode.unit_id || selectedNode.id}
                  unitName={selectedNode.name}
                  soldierIds={collectSoldierIds(selectedNode)}
                  reports={nodeReports}
                  suggestionId={activeSuggestionId}
                />
              )}

              {showEOINCREPBuilder && selectedNode && (
                <EOINCREPBuilder
                  unitId={selectedNode.unit_id || selectedNode.id}
                  unitName={selectedNode.name}
                  soldierIds={collectSoldierIds(selectedNode)}
                  reports={nodeReports}
                  suggestionId={activeSuggestionId}
                />
              )}

              {!selectedNode && !showReports && !showChat && (
                <Card className="neumorphic border-0 h-full flex items-center justify-center">
                  <div className="text-center text-muted-foreground">
                    <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="font-mono">
                      Select a unit or soldier to begin
                    </p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>

      <ReportDrawer
        selectedItem={selectedItem}
        onClose={() => setSelectedItem(null)}
      />
      <SummaryModal
        isOpen={showSummaryModal}
        onClose={() => setShowSummaryModal(false)}
      />
    </div>
  );
}
