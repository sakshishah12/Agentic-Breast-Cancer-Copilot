import { motion } from "framer-motion";
import AgentTrace from "./AgentTrace.jsx";
import { urgencyStyles } from "../lib/ui.js";

export default function DetailModal({ analysis, onClose }) {
  const riskPercent = Math.round(Number(analysis.risk_score || 0) * 100);
  const styles = urgencyStyles[analysis.urgency] || urgencyStyles.low;

  return (
    <motion.div
      className="fixed inset-0 z-50 grid place-items-center bg-black/35 px-4 py-6 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onMouseDown={onClose}
    >
      <motion.section
        role="dialog"
        aria-modal="true"
        aria-labelledby="analysis-detail-title"
        className="max-h-[92vh] w-full max-w-5xl overflow-hidden rounded-lg bg-[#fafafa] shadow-lift"
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 24, scale: 0.98 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-[#e5e5e5] bg-white px-5 py-5 sm:px-6">
          <div>
            <p className="text-sm font-medium text-[#737373]">{analysis.patientLabel}</p>
            <h2 id="analysis-detail-title" className="mt-1 text-2xl font-semibold text-[#202020]">
              Screening decision detail
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-3 py-2 text-sm font-semibold text-[#333333] transition hover:bg-[#eeeeee]"
          >
            Close
          </button>
        </div>

        <div className="max-h-[calc(92vh-88px)] overflow-y-auto p-5 sm:p-6">
          <div className="grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)]">
            <aside className="flex flex-col gap-4">
              <div className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
                <span className={`rounded-lg px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${styles.badge}`}>
                  {analysis.urgency} urgency
                </span>
                <p className="mt-5 text-6xl font-semibold leading-none text-[#202020]">{riskPercent}</p>
                <p className="mt-1 text-sm font-semibold uppercase tracking-[0.12em] text-[#737373]">risk score</p>
                <div className="mt-5 h-2 overflow-hidden rounded-full bg-[#ededed]">
                  <div className={`h-full rounded-full ${styles.bar}`} style={{ width: `${Math.min(riskPercent, 100)}%` }} />
                </div>
              </div>

              <div className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
                <p className="text-sm font-semibold text-[#333333]">Patient signals</p>
                <dl className="mt-4 flex flex-col gap-3 text-sm">
                  <Signal label="Age" value={analysis.patient?.age} />
                  <Signal label="Gender" value={analysis.patient?.gender} />
                  <Signal label="Smoker" value={analysis.patient?.smoker ? "Yes" : "No"} />
                  <Signal label="Family history" value={analysis.patient?.family_history ? "Yes" : "No"} />
                </dl>
                <div className="mt-4 flex flex-wrap gap-2">
                  {(analysis.patient?.symptoms || []).map((symptom) => (
                    <span key={symptom} className="rounded-lg bg-teal-50 px-3 py-2 text-xs font-semibold text-teal-800">
                      {symptom}
                    </span>
                  ))}
                </div>
              </div>
            </aside>

            <div className="flex min-w-0 flex-col gap-5">
              <section className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-[#202020]">Explanation</h3>
                  {analysis.needs_review ? (
                    <span className="rounded-lg bg-red-50 px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] text-red-700">
                      Clinician review
                    </span>
                  ) : null}
                </div>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-[#5f5f5f]">{analysis.explanation}</p>
              </section>

              <section className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
                <h3 className="text-lg font-semibold text-[#202020]">Recommendations</h3>
                <ul className="mt-3 flex flex-col gap-2 text-sm leading-6 text-[#5f5f5f]">
                  {(analysis.recommendations || []).map((recommendation, index) => (
                    <li key={`${recommendation}-${index}`} className="flex gap-2">
                      <span className="mt-2 size-1.5 shrink-0 rounded-full bg-teal-700" />
                      <span>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </section>

              <AgentTrace trace={analysis.agent_trace || []} />
            </div>
          </div>
        </div>
      </motion.section>
    </motion.div>
  );
}

function Signal({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-[#737373]">{label}</dt>
      <dd className="font-semibold capitalize text-[#202020]">{value || "None"}</dd>
    </div>
  );
}
