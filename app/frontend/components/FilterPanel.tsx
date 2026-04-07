"use client";

import { useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";

export interface Filters {
  category: string;
  color: string;
  size: string;
  occasion: string;
  budget_min: number;
  budget_max: number;
  brand: string;
  platforms: string[];
  gender: string;
}

interface FilterPanelProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  onReset: () => void;
  onSearch: () => void;
}

const CATEGORIES = [
  "", "shirts", "pants", "shoes", "watches",
  "accessories", "kurta", "dress", "jeans",
  "jacket", "saree", "bag", "belt"
];

const OCCASIONS = [
  "", "formal", "casual", "wedding", "party", "sports"
];

export default function FilterPanel({
  filters,
  onFiltersChange,
  onReset,
  onSearch,
}: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  const update = (key: keyof Filters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const handleMinBudget = (value: number) => {
    if (value < filters.budget_max - 100) {
      update("budget_min", value);
    }
  };

  const handleMaxBudget = (value: number) => {
    if (value > filters.budget_min + 100) {
      update("budget_max", value);
    }
  };

  return (
    <div className="bg-white border border-blue-100 rounded-xl shadow-sm overflow-hidden">

      {/* ✅ Only header is navy blue */}
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer bg-blue-900"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={18} className="text-blue-300" />
          <h2 className="font-semibold text-white">Filters</h2>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onReset();
          }}
          className="text-xs text-blue-300 hover:text-red-400 flex items-center gap-1 transition-colors"
        >
          <X size={12} />
          Reset
        </button>
      </div>

      {/* ✅ White body */}
      {isOpen && (
        <div className="px-4 pb-4 space-y-4 pt-4 bg-white">

          {/* Gender */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Gender
            </label>
            <div className="mt-2 flex gap-2">
              {["male", "female"].map((g) => (
                <button
                  key={g}
                  onClick={() =>
                    update("gender", filters.gender === g ? "" : g)
                  }
                  className={`flex-1 text-sm py-2 rounded-lg border font-medium transition-colors capitalize ${
                    filters.gender === g
                      ? "bg-blue-900 text-white border-blue-900"
                      : "bg-white text-gray-600 border-gray-300 hover:border-blue-400"
                  }`}
                >
                  {g === "male" ? "👨 Male" : "👩 Female"}
                </button>
              ))}
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => update("category", e.target.value)}
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
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
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Color
            </label>
            <input
              type="text"
              value={filters.color}
              onChange={(e) => update("color", e.target.value)}
              placeholder="navy blue, red, black..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
            />
          </div>

          {/* Size */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Size
            </label>
            <input
              type="text"
              value={filters.size}
              onChange={(e) => update("size", e.target.value)}
              placeholder="S, M, L, XL or shoe size..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
            />
          </div>

          {/* Occasion */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Occasion
            </label>
            <select
              value={filters.occasion}
              onChange={(e) => update("occasion", e.target.value)}
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
            >
              {OCCASIONS.map((o) => (
                <option key={o} value={o}>
                  {o || "Any Occasion"}
                </option>
              ))}
            </select>
          </div>

          {/* Budget Range */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Budget Range
            </label>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-sm font-semibold text-blue-900">
                ₹{filters.budget_min.toLocaleString()}
              </span>
              <span className="text-xs text-gray-400">to</span>
              <span className="text-sm font-semibold text-blue-900">
                ₹{filters.budget_max.toLocaleString()}
              </span>
            </div>

            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Min Price</span>
                <span>₹{filters.budget_min.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min={0}
                max={10000}
                step={100}
                value={filters.budget_min}
                onChange={(e) => handleMinBudget(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>

            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Max Price</span>
                <span>₹{filters.budget_max.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min={0}
                max={10000}
                step={100}
                value={filters.budget_max}
                onChange={(e) => handleMaxBudget(Number(e.target.value))}
                className="w-full accent-blue-900"
              />
            </div>

            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>₹0</span>
              <span>₹10,000</span>
            </div>
          </div>

          {/* Brand */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Brand (Optional)
            </label>
            <input
              type="text"
              value={filters.brand}
              onChange={(e) => update("brand", e.target.value)}
              placeholder="Allen Solly, Puma, Titan..."
              className="mt-1 w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 bg-white"
            />
          </div>

          {/* Platform */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Platform
            </label>
            <div className="mt-2">
              <span className="text-xs bg-blue-100 text-blue-800 px-3 py-1.5 rounded-full font-medium">
                🛒 Amazon India
              </span>
              <p className="text-xs text-gray-400 mt-2">
                Searching Amazon.in for best results
              </p>
            </div>
          </div>

          {/* Search Button */}
          <div className="pt-2">
            <button
              onClick={onSearch}
              className="w-full bg-blue-900 hover:bg-blue-800 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              🔍 Search with Filters
            </button>
          </div>

        </div>
      )}
    </div>
  );
}