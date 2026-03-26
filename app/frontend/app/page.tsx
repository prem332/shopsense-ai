"use client";

import { useState, useEffect } from "react";
import { ShoppingBag, Bell } from "lucide-react";
import ChatPanel from "@/components/ChatPanel";
import FilterPanel, { Filters } from "@/components/FilterPanel";
import ProductCard from "@/components/ProductCard";
import AlertsTab from "@/components/AlertsTab";
import { ChatResponse, Product } from "@/types";

const DEFAULT_FILTERS: Filters = {
  category: "",
  color: "",
  size: "",
  occasion: "",
  budget: 2000,
  brand: "",
  platforms: ["amazon", "flipkart", "myntra"],
};

const USER_ID = "user-123";

type Tab = "shop" | "alerts";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("shop");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [products, setProducts] = useState<Product[]>([]);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  
  const [sessionId, setSessionId] = useState<string>("default");
  useEffect(() => {
    setSessionId(`session-${Date.now()}`);
  }, []);

  const handleProductsReceived = (response: ChatResponse) => {
    setLastResponse(response);
    if (response.intent === "recommendation") {
      setProducts(response.products || []);
    }
  };

  const handleResetFilters = () => {
    setFilters(DEFAULT_FILTERS);
  };

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <ShoppingBag size={18} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-900 text-lg leading-none">
                ShopSense AI
              </h1>
              <p className="text-xs text-gray-500">
                Your personal AI stylist
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex bg-gray-100 rounded-xl p-1">
            <button
              onClick={() => setActiveTab("shop")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === "shop"
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              <ShoppingBag size={14} />
              Shop
            </button>
            <button
              onClick={() => setActiveTab("alerts")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === "alerts"
                  ? "bg-white text-indigo-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              <Bell size={14} />
              Alerts
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">

        {/* ── SHOP TAB ─────────────────────────────────── */}
        {activeTab === "shop" && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

            {/* Left: Filters */}
            <div className="lg:col-span-1">
              <FilterPanel
                filters={filters}
                onFiltersChange={setFilters}
                onReset={handleResetFilters}
              />
            </div>

            {/* Right: Chat + Products */}
            <div className="lg:col-span-3 space-y-6">

              {/* Chat Panel */}
              <ChatPanel
                filters={filters}
                onProductsReceived={handleProductsReceived}
                sessionId={sessionId}
                userId={USER_ID}
              />

              {/* Results Summary */}
              {lastResponse && lastResponse.intent === "recommendation" && (
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold text-gray-800">
                      {products.length > 0
                        ? `${products.length} Products Found`
                        : "No Products Found"
                      }
                    </h2>
                    {lastResponse.preferences && (
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {Object.entries(lastResponse.preferences)
                          .filter(([_, v]) => v !== null)
                          .map(([k, v]) => (
                            <span
                              key={k}
                              className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full"
                            >
                              {k}: {String(v)}
                            </span>
                          ))}
                      </div>
                    )}
                  </div>
                  {products.length > 0 && (
                    <p className="text-xs text-gray-400">
                      Attempts: {lastResponse.reflection_attempts}
                    </p>
                  )}
                </div>
              )}

              {/* Product Grid */}
              {products.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {products.map((product, index) => (
                    <ProductCard
                      key={`${product.title}-${index}`}
                      product={product}
                      rank={index + 1}
                    />
                  ))}
                </div>
              )}

              {/* Empty State */}
              {lastResponse &&
                lastResponse.intent === "recommendation" &&
                products.length === 0 && (
                <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
                  <ShoppingBag
                    size={48}
                    className="mx-auto text-gray-300 mb-4"
                  />
                  <p className="text-gray-500 font-medium">
                    No products found
                  </p>
                  <p className="text-gray-400 text-sm mt-1">
                    Try different keywords or adjust your filters
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── ALERTS TAB ────────────────────────────────── */}
        {activeTab === "alerts" && (
          <div className="max-w-2xl mx-auto">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-800">
                Price & Stock Alerts
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Set alerts and we'll notify you when conditions are met.
              </p>
            </div>
            <AlertsTab userId={USER_ID} />
          </div>
        )}
      </main>
    </div>
  );
}