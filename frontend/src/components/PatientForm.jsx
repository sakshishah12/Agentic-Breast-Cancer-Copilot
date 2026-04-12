import { useState } from "react";

const commonSymptoms = ["Cough", "Fatigue", "Weight loss", "Pain", "Bleeding", "Lump", "Fever"];

const initialForm = {
  age: "",
  gender: "female",
  smoker: false,
  family_history: false,
  symptoms: [],
};

export default function PatientForm({ onSubmit, isLoading }) {
  const [form, setForm] = useState(initialForm);
  const [symptomInput, setSymptomInput] = useState("");

  function addSymptom(symptom) {
    const cleanSymptom = symptom.trim();
    if (!cleanSymptom) return;

    setForm((current) => ({
      ...current,
      symptoms: current.symptoms.some((item) => item.toLowerCase() === cleanSymptom.toLowerCase())
        ? current.symptoms
        : [...current.symptoms, cleanSymptom],
    }));
    setSymptomInput("");
  }

  function removeSymptom(symptom) {
    setForm((current) => ({
      ...current,
      symptoms: current.symptoms.filter((item) => item !== symptom),
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    onSubmit({
      age: Number(form.age),
      gender: form.gender,
      smoker: form.smoker,
      family_history: form.family_history,
      symptoms: form.symptoms,
    });
  }

  return (
    <aside className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card lg:sticky lg:top-24">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">New analysis</p>
        <h2 className="mt-2 text-2xl font-semibold text-[#202020]">Patient intake</h2>
        <p className="mt-2 text-sm leading-6 text-[#666666]">
          Enter screening signals and send them to the copilot for risk scoring, guidance, and agent review.
        </p>
      </div>

      <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-[#333333]">Age</span>
          <input
            required
            min="1"
            max="120"
            type="number"
            value={form.age}
            onChange={(event) => setForm((current) => ({ ...current, age: event.target.value }))}
            className="rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-4 py-3 text-[#202020] transition focus:border-teal-600"
            placeholder="52"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-[#333333]">Gender</span>
          <select
            value={form.gender}
            onChange={(event) => setForm((current) => ({ ...current, gender: event.target.value }))}
            className="rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-4 py-3 text-[#202020] transition focus:border-teal-600"
          >
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="nonbinary">Nonbinary</option>
            <option value="other">Other</option>
          </select>
        </label>

        <div className="grid grid-cols-2 gap-3">
          <Toggle
            label="Smoker"
            checked={form.smoker}
            onChange={(checked) => setForm((current) => ({ ...current, smoker: checked }))}
          />
          <Toggle
            label="Family history"
            checked={form.family_history}
            onChange={(checked) => setForm((current) => ({ ...current, family_history: checked }))}
          />
        </div>

        <div className="flex flex-col gap-3">
          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-[#333333]">Symptoms</span>
            <div className="flex gap-2">
              <input
                type="text"
                value={symptomInput}
                onChange={(event) => setSymptomInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addSymptom(symptomInput);
                  }
                }}
                className="min-w-0 flex-1 rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-4 py-3 text-[#202020] transition focus:border-teal-600"
                placeholder="Add symptom"
              />
              <button
                type="button"
                onClick={() => addSymptom(symptomInput)}
                className="rounded-lg bg-[#202020] px-4 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5"
              >
                Add
              </button>
            </div>
          </label>

          <div className="flex flex-wrap gap-2">
            {commonSymptoms.map((symptom) => (
              <button
                key={symptom}
                type="button"
                onClick={() => addSymptom(symptom)}
                className="rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-3 py-2 text-xs font-medium text-[#4b4b4b] transition hover:border-teal-500 hover:text-teal-700"
              >
                {symptom}
              </button>
            ))}
          </div>

          {form.symptoms.length ? (
            <div className="flex flex-wrap gap-2">
              {form.symptoms.map((symptom) => (
                <button
                  key={symptom}
                  type="button"
                  onClick={() => removeSymptom(symptom)}
                  className="rounded-lg bg-teal-50 px-3 py-2 text-sm font-medium text-teal-800 transition hover:bg-teal-100"
                  aria-label={`Remove ${symptom}`}
                >
                  {symptom} x
                </button>
              ))}
            </div>
          ) : null}
        </div>

        <button
          type="submit"
          disabled={isLoading || !form.age}
          className="mt-1 flex min-h-12 items-center justify-center rounded-lg bg-teal-700 px-5 py-3 text-sm font-semibold text-white shadow-card transition hover:-translate-y-0.5 hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-[#a6a6a6]"
        >
          {isLoading ? <Spinner /> : "Analyze Patient"}
        </button>
      </form>
    </aside>
  );
}

function Toggle({ label, checked, onChange }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className="flex min-h-20 flex-col justify-between rounded-lg border border-[#d4d4d4] bg-[#fafafa] p-3 text-left transition hover:border-teal-500"
      aria-pressed={checked}
    >
      <span className="text-sm font-medium text-[#333333]">{label}</span>
      <span
        className={`relative h-6 w-11 rounded-full transition ${checked ? "bg-teal-700" : "bg-[#d6d5cf]"}`}
      >
        <span
          className={`absolute top-1 size-4 rounded-full bg-white shadow-sm transition ${
            checked ? "left-6" : "left-1"
          }`}
        />
      </span>
    </button>
  );
}

function Spinner() {
  return (
    <span className="size-5 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-label="Loading" />
  );
}
