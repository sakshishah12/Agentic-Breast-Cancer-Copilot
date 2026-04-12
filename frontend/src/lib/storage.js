const STORAGE_KEY = "agentic-cancer-screening-copilot:analyses";

export function loadAnalyses() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function saveAnalyses(analyses) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(analyses.slice(0, 48)));
  } catch {
    // Local persistence is helpful, but the app should keep working without it.
  }
}

