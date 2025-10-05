"use client";

import React, { useState, useEffect } from "react";
import {
  ChevronRight,
  ChevronDown,
  Users,
  Shield,
  Building2,
  User,
  Radio,
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

interface HierarchyNode {
  unit: Unit;
  children: HierarchyNode[];
  soldiers: Soldier[];
}

interface MilitaryHierarchyTreeProps {
  onNodeSelect: (node: any) => void;
  selectedNodeId?: string;
}

export function MilitaryHierarchyTree({
  onNodeSelect,
  selectedNodeId,
}: MilitaryHierarchyTreeProps) {
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHierarchy();
  }, []);

  const fetchHierarchy = async () => {
    try {
      const response = await await fetch(
        "https://military-hierarchy-backend.onrender.com//hierarchy"
      );
      const data = await response.json();

      // Transform the flat hierarchy data into a tree structure
      const tree = buildHierarchyTree(data.hierarchy);
      setHierarchy(tree);

      // Expand the top level by default
      const topLevelIds = tree.map((node) => node.unit.unit_id);
      setExpandedNodes(new Set(topLevelIds));
    } catch (error) {
      console.error("Error fetching hierarchy:", error);
    } finally {
      setLoading(false);
    }
  };

  const buildHierarchyTree = (hierarchy: any[]): HierarchyNode[] => {
    const nodeMap = new Map<string, HierarchyNode>();
    const rootNodes: HierarchyNode[] = [];

    // First pass: create all nodes
    hierarchy.forEach((unit: any) => {
      const node: HierarchyNode = {
        unit: {
          unit_id: unit.unit_id,
          name: unit.name,
          parent_unit_id: unit.parent_unit_id,
          level: unit.level,
          created_at: unit.created_at,
        },
        children: [],
        soldiers: unit.soldiers || [],
      };
      nodeMap.set(unit.unit_id, node);
    });

    // Second pass: build parent-child relationships
    hierarchy.forEach((unit: any) => {
      const node = nodeMap.get(unit.unit_id);
      if (node) {
        if (unit.parent_unit_id) {
          const parent = nodeMap.get(unit.parent_unit_id);
          if (parent) {
            parent.children.push(node);
          }
        } else {
          rootNodes.push(node);
        }
      }
    });

    return rootNodes;
  };

  const toggleExpanded = (nodeId: string) => {
    setExpandedNodes((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const getLevelIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case "battalion":
        return <Building2 className="h-4 w-4 text-blue-500" />;
      case "company":
        return <Shield className="h-4 w-4 text-green-500" />;
      case "platoon":
        return <Users className="h-4 w-4 text-orange-500" />;
      case "squad":
        return <User className="h-4 w-4 text-purple-500" />;
      default:
        return <Users className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "battalion":
        return "bg-military-blue/20 text-foreground border-military-blue/30";
      case "company":
        return "bg-military-olive/20 text-foreground border-military-olive/30";
      case "platoon":
        return "bg-military-amber/20 text-foreground border-military-amber/30";
      case "squad":
        return "bg-military-red/20 text-foreground border-military-red/30";
      default:
        return "bg-muted text-foreground border-border";
    }
  };

  const renderNode = (
    node: HierarchyNode,
    depth: number = 0
  ): React.ReactNode => {
    const isExpanded = expandedNodes.has(node.unit.unit_id);
    const isSelected = selectedNodeId === node.unit.unit_id;
    const hasChildren = node.children.length > 0;
    const hasSoldiers = node.soldiers.length > 0;

    return (
      <div key={node.unit.unit_id} className="select-none">
        {/* Unit Node */}
        <div
          className={`
            flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200
            ${
              isSelected
                ? "neumorphic-inset border-l-4 border-foreground"
                : "hover:bg-muted/50"
            }
          `}
          style={{ marginLeft: `${depth * 16}px` }}
          onClick={() => onNodeSelect(node)}
        >
          {/* Expand/Collapse Button */}
          <button
            className="mr-2 p-1 hover:bg-muted/50 rounded transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              if (hasChildren || hasSoldiers) {
                toggleExpanded(node.unit.unit_id);
              }
            }}
          >
            {hasChildren || hasSoldiers ? (
              isExpanded ? (
                <ChevronDown className="h-3 w-3 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-3 w-3 text-muted-foreground" />
              )
            ) : (
              <div className="w-3 h-3" />
            )}
          </button>

          {/* Unit Icon */}
          <div className="mr-2">{getLevelIcon(node.unit.level)}</div>

          {/* Unit Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm truncate text-foreground">
                {node.unit.name}
              </span>
              <span
                className={`
                px-2 py-0.5 text-xs rounded-full border font-medium font-mono
                ${getLevelColor(node.unit.level)}
              `}
              >
                {node.unit.level}
              </span>
            </div>
            <div className="text-xs text-muted-foreground font-mono">
              {node.children.length} subunits • {node.soldiers.length} personnel
            </div>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="ml-4">
            {/* Soldiers */}
            {hasSoldiers && (
              <div className="space-y-1">
                {node.soldiers.map((soldier) => (
                  <div
                    key={soldier.soldier_id}
                    className={`
                      flex items-center p-3 ml-4 rounded cursor-pointer transition-all duration-200
                      ${
                        selectedNodeId === soldier.soldier_id
                          ? "neumorphic-inset border-l-4 border-foreground"
                          : "hover:bg-muted/50"
                      }
                    `}
                    onClick={() => onNodeSelect(soldier)}
                  >
                    <Radio className="h-3 w-3 text-muted-foreground mr-2" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm truncate text-foreground">
                          {soldier.name}
                        </span>
                        <span className="px-1.5 py-0.5 text-xs bg-muted text-muted-foreground rounded font-mono">
                          {soldier.rank}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {soldier.device_id} • {soldier.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Child Units */}
            {node.children.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-card">
      <div className="p-6 border-b border-border bg-card/50">
        <h2 className="text-xl font-bold font-mono text-foreground">
          MILITARY HIERARCHY
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Click to view details and reports
        </p>
      </div>

      <div className="p-4">
        {hierarchy.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-2 text-muted-foreground/50" />
            <p className="font-mono">No hierarchy data available</p>
          </div>
        ) : (
          <div className="space-y-1">
            {hierarchy.map((node) => renderNode(node))}
          </div>
        )}
      </div>
    </div>
  );
}
