"use client";

import { useState, useEffect } from "react";
import { Bell, Trash2, Pause, Play, Plus, Loader2, AlertCircle } from "lucide-react";
import { getAlerts, createAlert, deleteAlert, pauseAlert } from "@/lib/api";
import { Alert } from "@/types";

interface AlertsTabProps {
  userId: string;
}

export default function AlertsTab({ userId }: AlertsTabProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [newAlertQuery, setNewAlertQuery] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAlerts();
  }, [userId]);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const response = await getAlerts(userId);
      setAlerts(response.alerts || []);
    } catch (err) {
      setError("Failed to load alerts");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAlert = async () => {
    if (!newAlertQuery.trim()) return;
    setIsCreating(true);
    try {
      await createAlert(userId, newAlertQuery);
      setNewAlertQuery("");
      setShowForm(false);
      await fetchAlerts();
    } catch (err) {
      setError("Failed to create alert");
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (alertId: string) => {
    try {
      await deleteAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      setError("Failed to delete alert");
    }
  };

  const handlePause = async (alertId: string) => {
    try {
      await pauseAlert(alertId);
      await fetchAlerts();
    } catch (err) {
      setError("Failed to pause alert");
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm">

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Bell size={18} className="text-indigo-600" />
          <h2 className="font-semibold text-gray-800">Price Alerts</h2>
          {alerts.length > 0 && (
            <span className="bg-indigo-100 text-indigo-700 text-xs font-medium px-2 py-0.5 rounded-full">
              {alerts.filter((a) => a.is_active).length} active
            </span>
          )}
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-3 py-1.5 rounded-lg transition-colors"
        >
          <Plus size={12} />
          New Alert
        </button>
      </div>

      {/* Create Alert Form */}
      {showForm && (
        <div className="p-4 border-b border-gray-100 bg-indigo-50">
          <p className="text-xs text-gray-600 mb-2">
            Describe what to monitor in plain English:
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={newAlertQuery}
              onChange={(e) => setNewAlertQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateAlert()}
              placeholder="alert when Allen Solly shirt drops below ₹999..."
              className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            />
            <button
              onClick={handleCreateAlert}
              disabled={isCreating || !newAlertQuery.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              {isCreating
                ? <Loader2 size={14} className="animate-spin" />
                : "Set Alert"
              }
            </button>
          </div>
          <div className="mt-2 flex gap-2 flex-wrap">
            {[
              "alert when price drops below ₹999",
              "notify when 40% discount",
              "alert when back in stock",
            ].map((example) => (
              <button
                key={example}
                onClick={() => setNewAlertQuery(example)}
                className="text-xs bg-white border border-gray-200 px-2 py-1 rounded-full hover:border-indigo-400 transition-colors text-gray-600"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mx-4 mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <AlertCircle size={14} className="text-red-500" />
          <p className="text-sm text-red-600">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">×</button>
        </div>
      )}

      {/* Alerts List */}
      <div className="p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={24} className="animate-spin text-indigo-600" />
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-8">
            <Bell size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 text-sm">No alerts yet</p>
            <p className="text-gray-400 text-xs mt-1">
              Create an alert to monitor prices
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`border rounded-xl p-4 transition-all ${
                  alert.is_active
                    ? "border-gray-200 bg-white"
                    : "border-gray-100 bg-gray-50 opacity-60"
                }`}
              >
                {/* Alert Header */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        alert.triggered_at
                          ? "bg-green-500"
                          : alert.is_active
                          ? "bg-yellow-500 animate-pulse"
                          : "bg-gray-400"
                      }`} />
                      <p className="text-sm font-medium text-gray-800">
                        {alert.product_name || "Product Alert"}
                      </p>
                    </div>

                    {/* Conditions */}
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {alert.brand && (
                        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                          {alert.brand}
                        </span>
                      )}
                      {alert.target_price && (
                        <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                          ≤ ₹{alert.target_price}
                        </span>
                      )}
                      {alert.discount_pct && (
                        <span className="text-xs bg-orange-50 text-orange-700 px-2 py-0.5 rounded-full">
                          {alert.discount_pct}%+ off
                        </span>
                      )}
                      {alert.in_stock && (
                        <span className="text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full">
                          In stock
                        </span>
                      )}
                      {alert.size && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                          Size {alert.size}
                        </span>
                      )}
                    </div>

                    {/* Platforms */}
                    {alert.platform && (
                      <p className="text-xs text-gray-400 mt-2">
                        📍 {alert.platform.map((p) =>
                          p.charAt(0).toUpperCase() + p.slice(1)
                        ).join(" · ")}
                      </p>
                    )}

                    {/* Status */}
                    <p className="text-xs text-gray-400 mt-1">
                      {alert.triggered_at
                        ? `✅ Triggered: ${new Date(alert.triggered_at).toLocaleDateString()}`
                        : alert.is_active
                        ? "⏰ Monitoring every 6 hours"
                        : "⏸️ Paused"
                      }
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-1 flex-shrink-0">
                    <button
                      onClick={() => handlePause(alert.id)}
                      title={alert.is_active ? "Pause" : "Resume"}
                      className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      {alert.is_active
                        ? <Pause size={14} />
                        : <Play size={14} />
                      }
                    </button>
                    <button
                      onClick={() => handleDelete(alert.id)}
                      title="Delete"
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}