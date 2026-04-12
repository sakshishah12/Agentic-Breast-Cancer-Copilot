import { motion } from "framer-motion";
import { urgencyStyles } from "../lib/ui.js";

export default function PatientCard({ analysis, onSelect }) {
  const riskPercent = Math.round(Number(analysis.risk_score || 0) * 100);
  const styles = urgencyStyles[analysis.urgency] || urgencyStyles.low;
  const recommendations = analysis.recommendations || [];

  return (
    <motion.article
      layout
      whileHover={{ y: -4, scale: 1.015 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="mb-4 inline-block w-full break-inside-avoid overflow-hidden rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card transition-shadow hover:shadow-lift"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-[#737373]">{analysis.patientLabel}</p>
          <div className="mt-2 flex items-end gap-2">
            <p className="text-5xl font-semibold leading-none text-[#202020]">{riskPercent}</p>
            <p className="pb-1 text-sm font-semibold uppercase tracking-[0.12em] text-[#737373]">risk</p>
          </div>
        </div>
        <span className={`rounded-lg px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${styles.badge}`}>
          {analysis.urgency}
        </span>
      </div>

      <div className="mt-5 h-2 overflow-hidden rounded-full bg-[#ededed]">
        <div className={`h-full rounded-full ${styles.bar}`} style={{ width: `${Math.min(riskPercent, 100)}%` }} />
      </div>

      <div className="mt-5">
        <p className="text-sm font-semibold text-[#333333]">Recommendations</p>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-6 text-[#5f5f5f]">
          {recommendations.slice(0, 3).map((recommendation, index) => (
            <li key={`${recommendation}-${index}`} className="flex gap-2">
              <span className="mt-2 size-1.5 shrink-0 rounded-full bg-teal-700" />
              <span>{recommendation}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-6 flex items-center justify-between gap-3">
        {analysis.needs_review ? (
          <span className="rounded-lg bg-red-50 px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] text-red-700">
            Needs review
          </span>
        ) : (
          <span className="rounded-lg bg-[#f0f8f7] px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] text-teal-800">
            Auto triaged
          </span>
        )}

        <button
          type="button"
          onClick={onSelect}
          className="rounded-lg bg-[#202020] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#3a3a36]"
        >
          View Details
        </button>
      </div>
    </motion.article>
  );
}
