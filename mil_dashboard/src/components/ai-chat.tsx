"use client";

import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { TreeNode } from "./hierarchy-tree";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  selectedNode: TreeNode | null;
  reports: any[];
}

export function AIChat({ selectedNode, reports }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Clear chat when node changes
    if (selectedNode) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content: `Hello! I'm your AI assistant for ${
            selectedNode.name
          }. I have access to ${reports.length} report(s) from this ${
            selectedNode.type
          }${
            selectedNode.type === "unit" ? " and its subordinates" : ""
          }. How can I help you analyze the situation?`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [selectedNode?.id]);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading || !selectedNode) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Prepare context from reports
      const reportsContext = reports.map((report) => {
        const structuredData =
          typeof report.structured_json === "string"
            ? JSON.parse(report.structured_json)
            : report.structured_json;

        return {
          type: report.report_type,
          time: report.timestamp,
          from: report.soldier_name || "Unknown",
          data: structuredData,
        };
      });

      // Call AI API (you'll need to implement this endpoint)
      const response = await fetch(
        "https://military-hierarchy-backend.onrender.com/ai/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: input,
            context: {
              node: selectedNode,
              reports: reportsContext,
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error("AI response failed");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          data.response || "I apologize, I couldn't process that request.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Fallback mock response for now
      const mockResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Based on the ${reports.length} reports from ${
          selectedNode.name
        }, I can help you analyze the current situation. The AI backend is not yet connected, but here's what I can see:\n\n${reports
          .slice(0, 3)
          .map((r) => `- ${r.report_type}: ${r.timestamp}`)
          .join(
            "\n"
          )}\n\nPlease implement the /ai/chat endpoint in the backend to enable full AI capabilities.`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, mockResponse]);
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

  if (!selectedNode) {
    return (
      <Card className="neumorphic border-0 h-full flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="font-mono">Select a node from the command structure</p>
          <p className="text-xs mt-2">to start an AI-powered conversation</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="neumorphic border-0 h-full flex flex-col">
      {/* Header */}
      <div className="p-2 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-military-blue" />
          <div className="flex-1">
            <h3 className="text-sm font-bold font-mono text-foreground">
              AI ASSISTANT
            </h3>
            <p className="text-[10px] text-muted-foreground font-mono">
              {selectedNode.name} ({reports.length} reports)
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3",
              message.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            {message.role === "assistant" && (
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-military-blue/20 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-military-blue" />
                </div>
              </div>
            )}

            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2",
                message.role === "user"
                  ? "bg-military-olive/20 border border-military-olive/30"
                  : "bg-muted/30 border border-border/30"
              )}
            >
              <p className="text-xs text-foreground whitespace-pre-wrap leading-tight">
                {message.content}
              </p>
              <p className="text-[10px] text-muted-foreground mt-0.5 font-mono">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>

            {message.role === "user" && (
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-military-olive/20 flex items-center justify-center">
                  <User className="h-4 w-4 text-military-olive" />
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 rounded-full bg-military-blue/20 flex items-center justify-center">
                <Loader2 className="h-4 w-4 text-military-blue animate-spin" />
              </div>
            </div>
            <div className="bg-muted/30 border border-border/30 rounded-lg px-4 py-2">
              <p className="text-xs text-muted-foreground">Thinking...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-2 border-t border-border/50">
        <div className="relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about the reports..."
            disabled={loading}
            className="neumorphic-inset border-0 pr-10 font-mono text-xs h-8"
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-1 top-1 h-6 w-6 bg-military-blue/20 text-foreground hover:bg-military-blue/30"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
}
