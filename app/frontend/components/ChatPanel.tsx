"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { sendChatMessage } from "@/lib/api";
import { ChatResponse } from "@/types";
import { Filters as FilterType } from "./FilterPanel";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  filters: FilterType;
  onProductsReceived: (response: ChatResponse) => void;
  sessionId: string;
  userId: string;
}

export default function ChatPanel({
  filters,
  onProductsReceived,
  sessionId,
  userId,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "👋 Hi! I'm ShopSense AI. Tell me what you're looking for, or use the filters on the left. I'll find the best products across Amazon, Flipkart, and Myntra!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const buildQueryFromFilters = (): string => {
    const parts: string[] = [];
    if (filters.brand) parts.push(filters.brand);
    if (filters.color) parts.push(filters.color);
    if (filters.category) parts.push(filters.category);
    if (filters.occasion) parts.push(`for ${filters.occasion}`);
    if (filters.size) parts.push(`size ${filters.size}`);
    if (filters.budget) parts.push(`under ₹${filters.budget}`);
    return parts.join(" ");
  };

  const sendMessage = async (queryOverride?: string) => {
    const query = queryOverride || input.trim();
    if (!query || isLoading) return;

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
        platforms: filters.platforms.length > 0
          ? filters.platforms
          : ["amazon", "flipkart", "myntra"],
      });

      const assistantContent = response.intent === "alert"
        ? response.response
        : `${response.response}\n\nScroll down to see the products! 🛍️`;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: assistantContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      onProductsReceived(response);

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "❌ Something went wrong. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterSearch = () => {
    const query = buildQueryFromFilters();
    if (query) sendMessage(query);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col h-[500px]">

      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b border-gray-100">
        <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <h2 className="font-semibold text-gray-800">ShopSense AI</h2>
          <p className="text-xs text-green-500">● Online</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            {/* Avatar */}
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.role === "user"
                ? "bg-indigo-100"
                : "bg-indigo-600"
            }`}>
              {message.role === "user"
                ? <User size={14} className="text-indigo-600" />
                : <Bot size={14} className="text-white" />
              }
            </div>

            {/* Bubble */}
            <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap ${
              message.role === "user"
                ? "bg-indigo-600 text-white rounded-tr-none"
                : "bg-gray-100 text-gray-800 rounded-tl-none"
            }`}>
              {message.content}
            </div>
          </div>
        ))}

        {/* Loading */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center">
              <Bot size={14} className="text-white" />
            </div>
            <div className="bg-gray-100 px-4 py-2.5 rounded-2xl rounded-tl-none">
              <Loader2 size={16} className="animate-spin text-indigo-600" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="e.g. Formal navy shirt size L under ₹1500..."
            className="flex-1 text-sm border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl transition-colors"
          >
            <Send size={16} />
          </button>
        </div>

        {/* Filter Search Button */}
        <button
          onClick={handleFilterSearch}
          disabled={isLoading}
          className="mt-2 w-full text-xs text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 py-1.5 rounded-lg transition-colors"
        >
          🔍 Search with filters above
        </button>
      </div>
    </div>
  );
}