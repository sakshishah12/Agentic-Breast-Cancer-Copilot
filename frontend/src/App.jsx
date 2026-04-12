import { useEffect, useMemo, useState } from "react";
import { AnimatePresence } from "framer-motion";
import Navbar from "./components/Navbar.jsx";
import PatientForm from "./components/PatientForm.jsx";
import MasonryGrid from "./components/MasonryGrid.jsx";
import DetailModal from "./components/DetailModal.jsx";
import FilterBar from "./components/FilterBar.jsx";
import { loadAnalyses, saveAnalyses } from "./lib/storage.js";

function normalizeApiBaseUrl(value) {
  if (!value) return "/api";
  if (value.startsWith("http://") || value.startsWith("https://") || value.startsWith("/")) {
    return value.replace(/\/$/, "");
  }
  return `https://${value.replace(/\/$/, "")}`;
}

const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
const API_URL = `${API_BASE_URL}/analyze`;

function buildPatientLabel(patient, index) {
  const gender = patient.gender ? `${patient.gender}` : "Patient";
  return `${gender}, ${patient.age || "unknown age"} - Case ${String(index + 1).padStart(2, "0")}`;
}

export default function App() {
  const [analyses, setAnalyses] = useState(() => loadAnalyses());
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [urgencyFilter, setUrgencyFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    saveAnalyses(analyses);
  }, [analyses]);

  const filteredAnalyses = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return analyses.filter((analysis) => {
      const urgencyMatch = urgencyFilter === "all" || analysis.urgency === urgencyFilter;
      const searchable = [
        analysis.patientLabel,
        analysis.urgency,
        analysis.explanation,
        ...(analysis.recommendations || []),
        ...(analysis.patient?.symptoms || []),
      ]
        .join(" ")
        .toLowerCase();

      return urgencyMatch && (!normalizedQuery || searchable.includes(normalizedQuery));
    });
  }, [analyses, query, urgencyFilter]);

  async function handleAnalyze(patient) {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(patient),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed with status ${response.status}`);
      }

      const result = await response.json();
      const nextAnalysis = {
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
        patient,
        patientLabel: buildPatientLabel(patient, analyses.length),
        ...result,
      };

      setAnalyses((current) => [nextAnalysis, ...current]);
      setSelectedAnalysis(nextAnalysis);
    } catch (analysisError) {
      setError(
        analysisError?.message ||
          "The analysis could not be completed. Confirm the API is available and the Render backend is healthy."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f7f7] text-[#202020]">
      <Navbar />

      <main className="mx-auto flex w-full max-w-[1520px] flex-col gap-8 px-4 pb-12 pt-6 sm:px-6 lg:px-8">
        <section className="grid gap-6 lg:grid-cols-[420px_minmax(0,1fr)] lg:items-start">
          <PatientForm onSubmit={handleAnalyze} isLoading={isLoading} />

          <div className="flex min-h-[280px] flex-col gap-5">
            <div className="flex flex-col gap-3">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">
                Patient decisions
              </p>
              <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
                <div>
                  <h1 className="max-w-3xl text-4xl font-semibold leading-tight text-[#202020] sm:text-5xl">
                    Agentic Cancer Screening Copilot
                  </h1>
                  <p className="mt-3 max-w-2xl text-base leading-7 text-[#5f5f5f]">
                    Capture risk signals, review AI recommendations, and inspect each tool call in one calm clinical workspace.
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-2 rounded-lg border border-[#e5e5e5] bg-white p-2 shadow-card">
                  <Metric label="Cases" value={analyses.length} />
                  <Metric label="Review" value={analyses.filter((item) => item.needs_review).length} />
                  <Metric label="High" value={analyses.filter((item) => item.urgency === "high").length} />
                </div>
              </div>
            </div>

            {error ? (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-800">
                {error}
              </div>
            ) : null}

            <FilterBar
              query={query}
              onQueryChange={setQuery}
              urgencyFilter={urgencyFilter}
              onUrgencyChange={setUrgencyFilter}
            />

            <MasonryGrid
              analyses={filteredAnalyses}
              isLoading={isLoading}
              onSelect={setSelectedAnalysis}
              hasAnyAnalyses={analyses.length > 0}
            />
          </div>
        </section>
      </main>

      <AnimatePresence>
        {selectedAnalysis ? (
          <DetailModal analysis={selectedAnalysis} onClose={() => setSelectedAnalysis(null)} />
        ) : null}
      </AnimatePresence>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="min-w-20 rounded-lg bg-[#f7f7f7] px-3 py-2 text-center">
      <p className="text-xl font-semibold text-[#202020]">{value}</p>
      <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#737373]">{label}</p>
    </div>
  );
}
