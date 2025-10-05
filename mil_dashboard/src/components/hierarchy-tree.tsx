"use client";

import { useState, useEffect } from "react";
import { ChevronRight, ChevronDown, Users, User, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";

interface Soldier {
  soldier_id: string;
  name: string;
  rank: string;
  unit_id: string;
  device_id: string;
  status: string;
}

interface Unit {
  unit_id: string;
  name: string;
  parent_unit_id: string | null;
  level: string;
  soldiers: Soldier[];
  subunits: Unit[];
}

interface HierarchyTreeProps {
  onNodeSelect: (node: TreeNode) => void;
  selectedNodeId?: string;
}

export interface TreeNode {
  id: string;
  name: string;
  type: "unit" | "soldier";
  level?: string;
  rank?: string;
  unit_id?: string;
  soldier_id?: string;
  children?: TreeNode[];
  soldiers?: Soldier[];
  subunits?: Unit[];
}

export function HierarchyTree({
  onNodeSelect,
  selectedNodeId,
}: HierarchyTreeProps) {
  const [hierarchyData, setHierarchyData] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchHierarchy();
  }, []);

  const fetchHierarchy = async () => {
    try {
      const response = await fetch(
        "https://military-hierarchy-backend.onrender.com/hierarchy"
      );
      const data = await response.json();

      // Build proper hierarchy from flat list
      const hierarchy = buildHierarchy(data.hierarchy || []);
      setHierarchyData(hierarchy);

      // Auto-expand first level
      if (hierarchy.length > 0) {
        const firstLevelIds = hierarchy.map((u: Unit) => u.unit_id);
        setExpandedNodes(new Set(firstLevelIds));
      }
    } catch (error) {
      console.error("Error fetching hierarchy:", error);
    } finally {
      setLoading(false);
    }
  };

  const buildHierarchy = (flatUnits: Unit[]): Unit[] => {
    const unitsMap = new Map<string, Unit>();
    const rootUnits: Unit[] = [];

    // First pass: create map of all units
    flatUnits.forEach((unit) => {
      unitsMap.set(unit.unit_id, {
        ...unit,
        soldiers: unit.soldiers || [],
        subunits: [],
      });
    });

    // Second pass: build parent-child relationships
    flatUnits.forEach((unit) => {
      const unitData = unitsMap.get(unit.unit_id);
      if (!unitData) return;

      if (unit.parent_unit_id === null) {
        rootUnits.push(unitData);
      } else {
        const parent = unitsMap.get(unit.parent_unit_id);
        if (parent) {
          parent.subunits.push(unitData);
        }
      }
    });

    return rootUnits;
  };

  const toggleNode = (nodeId: string) => {
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

  const convertUnitToTreeNode = (unit: Unit): TreeNode => {
    return {
      id: unit.unit_id,
      name: unit.name,
      type: "unit",
      level: unit.level,
      unit_id: unit.unit_id,
      soldiers: unit.soldiers || [],
      subunits: unit.subunits || [],
    };
  };

  const renderUnit = (unit: Unit, depth: number = 0) => {
    const isExpanded = expandedNodes.has(unit.unit_id);
    const isSelected = selectedNodeId === unit.unit_id;
    const hasChildren =
      (unit.soldiers?.length || 0) > 0 || (unit.subunits?.length || 0) > 0;

    return (
      <div key={unit.unit_id} className="select-none">
        <div
          className={cn(
            "flex items-center gap-2 px-3 py-2.5 rounded-md cursor-pointer transition-colors",
            "hover:bg-muted/50",
            isSelected && "bg-muted border-l-2 border-green-500"
          )}
          style={{ paddingLeft: `${depth * 20 + 12}px` }}
          onClick={(e) => {
            e.stopPropagation();
            onNodeSelect(convertUnitToTreeNode(unit));
          }}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(unit.unit_id);
              }}
              className="hover:bg-muted/50 p-0.5 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="h-3 w-3 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-3 w-3 text-muted-foreground" />
              )}
            </button>
          )}
          {!hasChildren && <div className="w-5" />}

          <Shield
            className={cn(
              "h-4 w-4",
              isSelected ? "text-green-500" : "text-muted-foreground"
            )}
          />
          <div className="flex-1">
            <div className="text-xs font-semibold font-mono text-foreground tracking-wide">
              {unit.name}
            </div>
            <div className="text-xs text-muted-foreground font-mono mt-0.5">
              {unit.level}
            </div>
          </div>
          <div className="text-xs text-muted-foreground font-mono">
            {unit.soldiers?.length || 0}x
          </div>
        </div>

        {isExpanded && (
          <div>
            {/* Render soldiers first */}
            {unit.soldiers?.map((soldier) =>
              renderSoldier(soldier, depth + 1, unit.unit_id)
            )}

            {/* Then render subunits */}
            {unit.subunits?.map((subunit) => renderUnit(subunit, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderSoldier = (soldier: Soldier, depth: number, unit_id: string) => {
    const isSelected = selectedNodeId === soldier.soldier_id;

    const soldierNode: TreeNode = {
      id: soldier.soldier_id,
      name: soldier.name,
      type: "soldier",
      rank: soldier.rank,
      soldier_id: soldier.soldier_id,
      unit_id: unit_id,
    };

    return (
      <div
        key={soldier.soldier_id}
        className={cn(
          "flex items-center gap-2 px-3 py-2.5 rounded-md cursor-pointer transition-colors",
          "hover:bg-muted/50",
          isSelected && "bg-muted border-l-2 border-blue-500"
        )}
        style={{ paddingLeft: `${depth * 20 + 32}px` }}
        onClick={() => onNodeSelect(soldierNode)}
      >
        <User
          className={cn(
            "h-4 w-4",
            isSelected ? "text-blue-500" : "text-muted-foreground"
          )}
        />
        <div className="flex-1">
          <div className="text-xs font-medium text-foreground tracking-wide">
            {soldier.name}
          </div>
          <div className="text-xs text-muted-foreground mt-0.5">
            {soldier.rank}
          </div>
        </div>
        <div
          className={cn(
            "h-2 w-2 rounded-full",
            soldier.status === "active" ? "bg-green-500" : "bg-muted-foreground"
          )}
        />
      </div>
    );
  };

  if (loading) {
    return (
      <Card className="neumorphic border-0 p-6">
        <div className="flex items-center justify-center text-muted-foreground text-sm">
          Loading command structure...
        </div>
      </Card>
    );
  }

  return (
    <Card className="neumorphic border-0 overflow-hidden h-full flex flex-col">
      <div className="p-5 border-b border-border/50">
        <h2 className="text-sm font-bold font-mono flex items-center gap-2 text-foreground tracking-wider">
          <Users className="h-4 w-4" />
          COMMAND STRUCTURE
        </h2>
        <p className="text-xs text-muted-foreground mt-1.5 font-mono">
          Select node to view reports & AI chat
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {hierarchyData.length === 0 ? (
          <div className="text-center text-muted-foreground text-sm py-8">
            No hierarchy data available
          </div>
        ) : (
          hierarchyData.map((unit) => renderUnit(unit, 0))
        )}
      </div>
    </Card>
  );
}
