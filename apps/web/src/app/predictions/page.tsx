"use client";

import { useState } from "react";
import { ModelSelector } from "@/components/predictions/ModelSelector";
import { PredictionForm } from "@/components/predictions/PredictionForm";
import { PredictionResults } from "@/components/predictions/PredictionResults";
import type { PredictionResponse } from "@/types/predictions";

export default function PredictionsPage() {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] =
    useState<PredictionResponse | null>(null);

  const handleModelSelect = (modelName: string) => {
    setSelectedModel(modelName);
    setPredictionResult(null); // Clear previous results when changing models
  };

  const handlePredict = (result: PredictionResponse) => {
    setPredictionResult(result);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ML Predictions
          </h1>
          <p className="text-gray-600">
            Select a model and input parameters to generate predictions using
            our trained machine learning models.
          </p>
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <ModelSelector
            selectedModel={selectedModel}
            onModelSelect={handleModelSelect}
          />
        </div>

        {/* Prediction Form and Results */}
        {selectedModel && (
          <div className="grid lg:grid-cols-2 gap-6">
            <div>
              <PredictionForm
                modelName={selectedModel}
                onPredict={handlePredict}
              />
            </div>
            <div>
              {predictionResult ? (
                <PredictionResults
                  modelName={selectedModel}
                  result={predictionResult}
                />
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
                  <div className="text-gray-400 mb-2">
                    <svg
                      className="mx-auto h-12 w-12"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>
                  <p className="text-gray-500">
                    Fill in the form and click &quot;Make Prediction&quot; to
                    see results
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Model Information */}
        {!selectedModel && (
          <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Available Models
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">
                  Tyre Degradation
                </h3>
                <p className="text-sm text-gray-600">
                  Predicts the degradation rate (seconds/lap) for a given stint
                  based on compound and driver characteristics.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Lap Time</h3>
                <p className="text-sm text-gray-600">
                  Predicts lap time based on tyre age, compound, track status,
                  position, and driver.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">
                  Overtake Probability
                </h3>
                <p className="text-sm text-gray-600">
                  Predicts the probability of an overtake occurring in the next
                  3 laps based on gap, closing rate, tyre advantage, and DRS
                  availability.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Race Result</h3>
                <p className="text-sm text-gray-600">
                  Predicts finishing position based on grid position, expected
                  average lap time, and driver characteristics.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
