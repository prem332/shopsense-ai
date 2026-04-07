"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { sendChatMessage } from "@/lib/api";
import { ChatResponse } from "@/types";
import { Filters } from "./FilterPanel";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  filters: Filters;
  onProductsReceived: (response: ChatResponse) => void;
  sessionId: string;
  userId: string;
  externalQuery?: string;
  onExternalQueryHandled?: () => void;
}

export default function ChatPanel({
  filters,
  onProductsReceived,
  sessionId,
  userId,
  externalQuery,
  onExternalQueryHandled,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "👋 Hi! I'm ShopSense AI. Tell me what you're looking for, or use the filters on the left. I'll find the best products from Amazon!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ Handle filter search from FilterPanel
  useEffect(() => {
    if (externalQuery && externalQuery.trim()) {
      sendMessage(externalQuery);
      if (onExternalQueryHandled) onExternalQueryHandled();
    }
  }, [externalQuery]);

  const buildAssistantMessage = (response: ChatResponse): string => {
    if (response.intent === "alert") {
      return response.response;
    }

    // ✅ Show rejection message for invalid queries
    if (response.is_valid === false) {
      return response.response;
    }

    if (response.products_count === 0) {
      const budgetInfo =
        filters.budget_min > 0
          ? `₹${filters.budget_min.toLocaleString()} — ₹${filters.budget_max.toLocaleString()}`
          : `under ₹${filters.budget_max.toLocaleString()}`;
      return (
        `❌ No products found in your budget range (${budgetInfo}).\n\n` +
        `💡 Try:\n` +
        `• Lower the minimum price\n` +
        `• Increase the maximum price\n` +
        `• Use broader keywords\n` +
        `• Remove some filters`
      );
    }

    return `${response.response}\n\nScroll down to see the products! 🛍️`;
  };

  const sendMessage = async (queryOverride?: string) => {
    const query = queryOverride || input.trim();
    if (!query || isLoading) return;

    // ✅ Clear old products before new search
    onProductsReceived({
      status: "loading",
      intent: "recommendation",
      is_valid: true,
      preferences: {},
      products: [],
      products_count: 0,
      reflection_attempts: 0,
      alert_id: null,
      response: ""
    } as any);

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage(query, {
        userId,
        sessionId,
        platforms: ["amazon"],
        budget_min: filters.budget_min,
        budget_max: filters.budget_max,
        gender: filters.gender,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: buildAssistantMessage(response),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      onProductsReceived(response);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "❌ Something went wrong. Please check if the backend is running and try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // ✅ White body, navy header
    <div className="bg-white border border-blue-100 rounded-xl shadow-sm flex flex-col h-[500px] overflow-hidden">

      {/* ✅ Navy blue header strip */}
      <div className="flex items-center gap-3 px-4 py-3 bg-blue-900">
        <div className="w-8 h-8 bg-blue-700 rounded-full flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-white">ShopSense AI</h2>
          <p className="text-xs text-green-400">● Online</p>
        </div>

        {/* Active filters indicator */}
        {(filters.budget_min > 0 || filters.gender || filters.category) && (
          <div className="ml-auto flex flex-wrap gap-1">
            {filters.gender && (
              <span className="text-xs bg-blue-700 text-blue-200 px-2 py-0.5 rounded-full capitalize">
                {filters.gender}
              </span>
            )}
            {filters.category && (
              <span className="text-xs bg-blue-700 text-blue-200 px-2 py-0.5 rounded-full capitalize">
                {filters.category}
              </span>
            )}
            {filters.budget_min > 0 && (
              <span className="text-xs bg-green-800 text-green-300 px-2 py-0.5 rounded-full">
                ₹{filters.budget_min.toLocaleString()}–
                ₹{filters.budget_max.toLocaleString()}
              </span>
            )}
          </div>
        )}
      </div>

      {/* ✅ White messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === "user"
                  ? "bg-blue-900"
                  : "bg-blue-100"
              }`}
            >
              {message.role === "user" ? (
                <User size={14} className="text-white" />
              ) : (
                <Bot size={14} className="text-blue-700" />
              )}
            </div>

            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap ${
                message.role === "user"
                  ? "bg-blue-900 text-white rounded-tr-none"
                  : "bg-blue-50 text-gray-800 rounded-tl-none"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center">
              <Bot size={14} className="text-blue-700" />
            </div>
            <div className="bg-blue-50 px-4 py-3 rounded-2xl rounded-tl-none flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-blue-600" />
              <span className="text-xs text-gray-500">
                Searching Amazon...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ✅ White input area */}
      <div className="p-4 border-t border-blue-100 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="e.g. I am a male, blue shirt size M between 1500 and 6000..."
            className="flex-1 text-sm border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || !input.trim()}
            className="bg-blue-900 hover:bg-blue-800 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}