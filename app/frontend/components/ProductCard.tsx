"use client";

import { Product } from "@/types";
import { Star, ExternalLink, ShoppingCart } from "lucide-react";

interface ProductCardProps {
  product: Product;
  rank: number;
}

const platformColors: Record<string, string> = {
  Amazon: "bg-orange-100 text-orange-700",
  Flipkart: "bg-blue-100 text-blue-700",
  Myntra: "bg-pink-100 text-pink-700",
};

export default function ProductCard({ product, rank }: ProductCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden flex flex-col">

      {/* Rank Badge */}
      <div className="relative">
        <div className="absolute top-2 left-2 z-10 bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded-full">
          #{rank}
        </div>

        {/* Platform Badge */}
        <div className={`absolute top-2 right-2 z-10 text-xs font-semibold px-2 py-1 rounded-full ${platformColors[product.platform] || "bg-gray-100 text-gray-700"}`}>
          {product.platform}
        </div>

        {/* Product Image */}
        {product.image ? (
          <img
            src={product.image}
            alt={product.title}
            className="w-full h-48 object-contain bg-gray-50 p-4"
            onError={(e) => {
              (e.target as HTMLImageElement).src = "/placeholder.png";
            }}
          />
        ) : (
          <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
            <ShoppingCart className="text-gray-400" size={48} />
          </div>
        )}
      </div>

      {/* Product Details */}
      <div className="p-4 flex flex-col flex-1">
        {/* Title */}
        <h3 className="text-sm font-medium text-gray-800 line-clamp-2 mb-2 flex-1">
          {product.title}
        </h3>

        {/* Price + Rating */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-lg font-bold text-green-600">
            {product.price}
          </span>

          {product.rating && product.rating !== "N/A" && (
            <div className="flex items-center gap-1">
              <Star size={14} className="text-yellow-500 fill-yellow-500" />
              <span className="text-sm text-gray-600">{product.rating}</span>
            </div>
          )}
        </div>


        {/* Buy Button */}
        <a
          href={product.link}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
        >
          <ExternalLink size={14} />
          Buy Now
        </a>
      </div>
    </div>
  );
}