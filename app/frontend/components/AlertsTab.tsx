"use client";

import { useState, useEffect } from "react";
import { Bell, Plus, Trash2, Pause, Play } from "lucide-react";

interface Alert {
  id: string;
  user_id: string;
  product_name: string;
  conditions: {
    brand?: string;
    target_price?: number;
    discount_pct?: number;
    in_stock?: boolean;
    color?: string;
    size?: string;
    platforms?: string[];
  };
  status: string;
  created_at: string;
}

interface AlertsTabProps {
  userId: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AlertsTab({ userId }: AlertsTabProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [alertQuery, setAlertQuery] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/alerts/${userId}`);
      const data = await res.json();
      if (data.status === "success") {
        setAlerts(data.alerts || []);
      }
    } catch (err) {
      setError("Failed to load alerts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [userId]);

  const handleCreateAlert = async () => {
    if (!alertQuery.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/api/alerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, user_query: alertQuery }),
      });
      const data = await res.json();
      if (data.status === "success") {
        setAlertQuery("");
        setShowForm(false);
        fetchAlerts();
      }
    } catch (err) {
      setError("Failed to create alert");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/alerts/${alertId}`, {
        method: "DELETE",
      });
      const data = await res.json();
      if (data.status === "success") {
        fetchAlerts();
      }
    } catch (err) {
      setError("Failed to delete alert");
    }
  };

  const handleToggleAlert = async (alertId: string, currentStatus: string) => {
    const newStatus = currentStatus === "active" ? "paused" : "active";
    try {
      const res = await fetch(`${API_BASE}/api/alerts/${alertId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      const data = await res.json();
      if (data.status === "success") {
        fetchAlerts();
      }
    } catch (err) {
      setError("Failed to update alert");
    }
  };

  const activeAlerts = alerts.filter((a) => a.status === "active");

  const EXAMPLE_QUERIES = [
    "alert when price drops below ₹999",
    "notify when 40% discount",
    "alert when back in stock",
  ];

  return (
    // ✅ White panel with navy accents
    <div className="bg-white border border-blue-100 rounded-xl shadow-sm overflow-hidden">

      {/* ✅ Navy blue header strip */}
      <div className="flex items-center justify-between px-4 py-3 bg-blue-900">
        <div className="flex items-center gap-2">
          <Bell size={18} className="text-blue-300" />
          <h3 className="font-semibold text-white">Price Alerts</h3>
          {activeAlerts.length > 0 && (
            <span className="text-xs bg-blue-700 text-blue-200 px-2 py-0.5 rounded-full">
              {activeAlerts.length} active
            </span>
          )}
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1.5 text-sm bg-white text-blue-900 px-3 py-1.5 rounded-lg font-medium hover:bg-blue-50 transition-colors"
        >
          <Plus size={14} />
          New Alert
        </button>
      </div>

      {/* Create Alert Form */}
      {showForm && (
        <div className="p-4 border-b border-blue-100 bg-blue-50">
          <p className="text-xs text-gray-500 mb-2">
            Describe what to monitor in plain English:
          </p>
          <input
            type="text"
            value={alertQuery}
            onChange={(e) => setAlertQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreateAlert()}
            placeholder="alert when Allen Solly shirt drops below ₹999..."
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3 bg-white text-gray-800"
          />
          <div className="flex flex-wrap gap-2 mb-3">
            {EXAMPLE_QUERIES.map((q) => (
              <button
                key={q}
                onClick={() => setAlertQuery(q)}
                className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full hover:bg-blue-200 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
          <button
            onClick={handleCreateAlert}
            disabled={submitting || !alertQuery.trim()}
            className="w-full bg-blue-900 text-white font-medium text-sm py-2 rounded-lg hover:bg-blue-800 disabled:opacity-50 transition-colors"
          >
            {submitting ? "Setting Alert..." : "Set Alert"}
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mx-4 mt-3 text-xs text-red-600 bg-red-50 px-3 py-2 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      {/* Alerts List */}
      <div className="p-4 space-y-3 bg-white">
        {loading ? (
          <div className="text-center py-8 text-gray-400">
            Loading alerts...
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell size={40} className="mx-auto text-blue-200 mb-3" />
            <p className="text-gray-500 font-medium">No alerts yet</p>
            <p className="text-gray-400 text-xs mt-1">
              Create an alert to monitor prices
            </p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-blue-50 rounded-xl p-4 border ${
                alert.status === "active"
                  ? "border-blue-200"
                  : "border-gray-200 opacity-60"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 mt-1 ${
                      alert.status === "active"
                        ? "bg-green-500"
                        : "bg-gray-400"
                    }`}
                  />
                  <div>
                    <p className="text-sm font-medium text-gray-800 capitalize">
                      {alert.product_name || "Product Alert"}
                    </p>

                    {/* Conditions */}
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {alert.conditions?.brand && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                          {alert.conditions.brand}
                        </span>
                      )}
                      {alert.conditions?.target_price && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                          ≤ ₹{alert.conditions.target_price}
                        </span>
                      )}
                      {alert.conditions?.discount_pct && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                          {alert.conditions.discount_pct}% off
                        </span>
                      )}
                      {alert.conditions?.in_stock && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                          In Stock
                        </span>
                      )}
                    </div>

                    {/* Meta */}
                    <div className="flex gap-3 mt-2">
                      <p className="text-xs text-gray-400 flex items-center gap-1">
                        📍 Amazon
                      </p>
                      <p className="text-xs text-gray-400 flex items-center gap-1">
                        🕐 Every 6 hours
                      </p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button
                    onClick={() => handleToggleAlert(alert.id, alert.status)}
                    className="p-1.5 text-gray-400 hover:text-blue-700 hover:bg-blue-100 rounded-lg transition-colors"
                    title={alert.status === "active" ? "Pause" : "Resume"}
                  >
                    {alert.status === "active" ? (
                      <Pause size={14} />
                    ) : (
                      <Play size={14} />
                    )}
                  </button>
                  <button
                    onClick={() => handleDeleteAlert(alert.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}