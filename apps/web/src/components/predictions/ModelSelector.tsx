"use client";

import { useEffect, useState } from "react";
import { fetchModels } from "@/lib/api/predictions";
import type { Model } from "@/types/predictions";
import { Card } from "@/components/ui/Card";

interface ModelSelectorProps {
  selectedModel: string | null;
  onModelSelect: (modelName: string) => void;
}

export function ModelSelector({
  selectedModel,
  onModelSelect,
}: ModelSelectorProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchModels(undefined, "active");
        setModels(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load models");
      } finally {
        setLoading(false);
      }
    };

    loadModels();
  }, []);

  if (loading) {
    return (
      <Card title="Select Model">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading models...</div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Select Model">
        <div className="flex items-center justify-center py-12">
          <div className="text-red-500">Error: {error}</div>
        </div>
      </Card>
    );
  }

  // Group models by name (latest version only)
  const latestModels = models.reduce((acc, model) => {
    if (!acc[model.model_name] || model.created_at > acc[model.model_name].created_at) {
      acc[model.model_name] = model;
    }
    return acc;
  }, {} as Record<string, Model>);

  const modelList = Object.values(latestModels);

  const modelDisplayNames: Record<string, string> = {
    tyre_degradation: "Tyre Degradation",
    lap_time: "Lap Time",
    overtake: "Overtake Probability",
    race_result: "Race Result",
  };

  const modelDescriptions: Record<string, string> = {
    tyre_degradation: "Predict tyre degradation rate (s/lap)",
    lap_time: "Predict lap time for given conditions",
    overtake: "Predict probability of overtake",
    race_result: "Predict finishing position",
  };

  return (
    <Card title="Select Model">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modelList.map((model) => (
          <button
            key={model.id}
            onClick={() => onModelSelect(model.model_name)}
            className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
              selectedModel === model.model_name
                ? "border-red-600 bg-red-50"
                : "border-gray-200 hover:border-red-300"
            }`}
          >
            <h3 className="font-bold text-lg mb-1">
              {modelDisplayNames[model.model_name] || model.model_name}
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              {modelDescriptions[model.model_name] || "ML prediction model"}
            </p>
            <div className="text-xs text-gray-500 mb-2">
              v{model.version} • {model.model_type}
            </div>
            <div className="text-xs text-gray-700 space-y-1">
              {Object.entries(model.metrics).slice(0, 3).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="font-medium">{key}:</span>
                  <span>
                    {typeof value === "number" ? value.toFixed(3) : value}
                  </span>
                </div>
              ))}
            </div>
          </button>
        ))}
      </div>
      {modelList.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No models available. Train models first using the training scripts.
        </div>
      )}
    </Card>
  );
}
