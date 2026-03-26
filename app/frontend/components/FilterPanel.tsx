"use client";

import { useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";

export interface Filters {
  category: string;
  color: string;
  size: string;
  occasion: string;
  budget: number;
  brand: string;
  platforms: string[];
}

interface FilterPanelProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  onReset: () => void;
}

const CATEGORIES = ["", "shirts", "pants", "shoes", "watches", "accessories", "kurta", "dress"];
const OCCASIONS = ["", "formal", "casual", "wedding", "party", "sports"];
const PLATFORMS = ["amazon", "flipkart", "myntra"];

export default function FilterPanel({
  filters,
  onFiltersChange,
  onReset,
}: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  const update = (key: keyof Filters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const togglePlatform = (platform: string) => {
    const current = filters.platforms;
    const updated = current.includes(platform)
      ? current.filter((p) => p !== platform)
      : [...current, platform];
    update("platforms", updated);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm">

      {/* Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Filters</h2>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); onReset(); }}
          className="text-xs text-gray-500 hover:text-red-500 flex items-center gap-1"
        >
          <X size={12} />
          Reset
        </button>
      </div>

      {isOpen && (
        <div className="px-4 pb-4 space-y-4 border-t border-gray-100 pt-4">

          {/* Category */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => update("category", e.target.value)}
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c || "All Categories"}
                </option>
              ))}
            </select>
          </div>

          {/* Color */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Color
            </label>
            <input
              type="text"
              value={filters.color}
              onChange={(e) => update("color", e.target.value)}
              placeholder="navy blue, red, black..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Size */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Size
            </label>
            <input
              type="text"
              value={filters.size}
              onChange={(e) => update("size", e.target.value)}
              placeholder="S, M, L, XL or shoe size..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Occasion */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Occasion
            </label>
            <select
              value={filters.occasion}
              onChange={(e) => update("occasion", e.target.value)}
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {OCCASIONS.map((o) => (
                <option key={o} value={o}>
                  {o || "Any Occasion"}
                </option>
              ))}
            </select>
          </div>

          {/* Budget */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Max Budget: ₹{filters.budget.toLocaleString()}
            </label>
            <input
              type="range"
              min={200}
              max={10000}
              step={100}
              value={filters.budget}
              onChange={(e) => update("budget", Number(e.target.value))}
              className="mt-2 w-full accent-indigo-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>₹200</span>
              <span>₹10,000</span>
            </div>
          </div>

          {/* Brand */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Brand (optional)
            </label>
            <input
              type="text"
              value={filters.brand}
              onChange={(e) => update("brand", e.target.value)}
              placeholder="Allen Solly, Puma, Titan..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Platforms */}
          <div>
            <label className="text-xs font-medium text-gray-600 uppercase tracking-wide">
              Platforms
            </label>
            <div className="mt-2 flex gap-2 flex-wrap">
              {PLATFORMS.map((platform) => (
                <button
                  key={platform}
                  onClick={() => togglePlatform(platform)}
                  className={`text-xs px-3 py-1.5 rounded-full border font-medium transition-colors ${
                    filters.platforms.includes(platform)
                      ? "bg-indigo-600 text-white border-indigo-600"
                      : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400"
                  }`}
                >
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}