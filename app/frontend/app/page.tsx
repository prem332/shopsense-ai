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
  budget_min: 0,
  budget_max: 2000,
  brand: "",
  platforms: ["amazon"],
  gender: "",
};

const USER_ID = "user-123";
type Tab = "shop" | "alerts";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("shop");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [products, setProducts] = useState<Product[]>([]);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const [sessionId, setSessionId] = useState<string>("default");
  const [chatQuery, setChatQuery] = useState<string>("");

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

  const handleFilterSearch = () => {
    const parts: string[] = [];
    if (filters.gender) parts.push(`${filters.gender}'s`);
    if (filters.brand) parts.push(filters.brand);
    if (filters.color) parts.push(filters.color);
    if (filters.category) parts.push(filters.category);
    if (filters.occasion) parts.push(`for ${filters.occasion}`);
    if (filters.size) parts.push(`size ${filters.size}`);
    const query = parts.join(" ") || "products";
    setChatQuery(query);
  };

  return (
    // ✅ Navy Blue background
    <div className="min-h-screen bg-blue-50">

      {/* ✅ Navy Blue Header */}
      <header className="bg-blue-900 sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
              <ShoppingBag size={20} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-white text-lg leading-none">
                ShopSense AI
              </h1>
              <p className="text-blue-300 text-xs">
                Your personal AI stylist
              </p>
            </div>
          </div>

          {/* ✅ Navy Tab Switcher */}
          <div className="flex bg-blue-800 rounded-xl p-1 gap-1">
            <button
              onClick={() => setActiveTab("shop")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === "shop"
                  ? "bg-white text-blue-900 shadow-sm"
                  : "text-blue-200 hover:text-white"
              }`}
            >
              <ShoppingBag size={14} />
              Shop
            </button>
            <button
              onClick={() => setActiveTab("alerts")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === "alerts"
                  ? "bg-white text-blue-900 shadow-sm"
                  : "text-blue-200 hover:text-white"
              }`}
            >
              <Bell size={14} />
              Alerts
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">

        {activeTab === "shop" && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

            {/* Filter Panel */}
            <div className="lg:col-span-1">
              <FilterPanel
                filters={filters}
                onFiltersChange={setFilters}
                onReset={handleResetFilters}
                onSearch={handleFilterSearch}
              />
            </div>

            {/* Chat + Products */}
            <div className="lg:col-span-3 space-y-6">

              <ChatPanel
                filters={filters}
                onProductsReceived={handleProductsReceived}
                sessionId={sessionId}
                userId={USER_ID}
                externalQuery={chatQuery}
                onExternalQueryHandled={() => setChatQuery("")}
              />

              {/* Results Summary */}
              {lastResponse &&
                lastResponse.intent === "recommendation" && (
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="font-semibold text-blue-900">
                        {products.length > 0
                          ? `${products.length} Products Found`
                          : "No Products Found"}
                      </h2>
                      {lastResponse.preferences && (
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {Object.entries(lastResponse.preferences)
                            .filter(([_, v]) => v !== null)
                            .map(([k, v]) => (
                              <span
                                key={k}
                                className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full"
                              >
                                {k}: {String(v)}
                              </span>
                            ))}
                        </div>
                      )}
                    </div>
                    {products.length > 0 && (
                      <p className="text-xs text-blue-400">
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
                  <div className="text-center py-16 bg-white rounded-xl border border-blue-100">
                    <ShoppingBag
                      size={48}
                      className="mx-auto text-blue-200 mb-4"
                    />
                    <p className="text-blue-400 font-medium">
                      No products found
                    </p>
                    <p className="text-blue-300 text-sm mt-1">
                      Try adjusting your filters or budget range
                    </p>
                  </div>
                )}
            </div>
          </div>
        )}

        {activeTab === "alerts" && (
          <div className="max-w-2xl mx-auto">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-blue-900">
                Price & Stock Alerts
              </h2>
              <p className="text-sm text-blue-400 mt-1">
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