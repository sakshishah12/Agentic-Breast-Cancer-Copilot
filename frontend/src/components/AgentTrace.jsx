import { useState } from "react";

export default function AgentTrace({ trace }) {
  if (!trace.length) {
    return (
      <section className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
        <h3 className="text-lg font-semibold text-[#202020]">Agent trace</h3>
        <p className="mt-3 text-sm leading-6 text-[#666666]">No agent tool calls were returned for this analysis.</p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#202020]">Agent trace</h3>
          <p className="mt-1 text-sm text-[#737373]">Tool calls, inputs, and outputs from the screening workflow.</p>
        </div>
        <span className="rounded-lg bg-[#f0f8f7] px-3 py-2 text-xs font-bold uppercase tracking-[0.12em] text-teal-800">
          {trace.length} steps
        </span>
      </div>

      <ol className="mt-5 flex flex-col gap-4">
        {trace.map((step, index) => (
          <TraceStep key={`${step.tool}-${index}`} step={step} index={index} />
        ))}
      </ol>
    </section>
  );
}

function TraceStep({ step, index }) {
  const [expanded, setExpanded] = useState(index === 0);
  const preview = formatPreview(step.output);

  return (
    <li className="relative pl-8">
      <span className="absolute left-0 top-1 grid size-6 place-items-center rounded-full bg-[#202020] text-xs font-semibold text-white">
        {index + 1}
      </span>
      <span className="absolute bottom-[-18px] left-3 top-8 w-px bg-[#e5e5e5]" aria-hidden="true" />

      <div className="rounded-lg border border-[#e5e5e5] bg-[#fafafa] p-4">
        <button
          type="button"
          onClick={() => setExpanded((current) => !current)}
          className="flex w-full items-start justify-between gap-4 text-left"
          aria-expanded={expanded}
        >
          <span>
            <span className="text-xs font-bold uppercase tracking-[0.14em] text-teal-700">Step {index + 1}</span>
            <span className="mt-1 block break-words text-base font-semibold text-[#202020]">
              {step.tool || "agent_tool"}
            </span>
            <span className="mt-1 block break-words text-sm leading-6 text-[#666666]">{preview}</span>
          </span>
          <span className="rounded-lg border border-[#d4d4d4] bg-white px-3 py-2 text-xs font-semibold text-[#4b4b4b]">
            {expanded ? "Hide" : "Open"}
          </span>
        </button>

        {expanded ? (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <TraceBlock title="Input" value={step.input} />
            <TraceBlock title="Output" value={step.output} />
          </div>
        ) : null}
      </div>
    </li>
  );
}

function TraceBlock({ title, value }) {
  return (
    <div className="min-w-0 rounded-lg border border-[#e5e5e5] bg-white p-3">
      <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#737373]">{title}</p>
      <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#333333]">
        {JSON.stringify(value ?? null, null, 2)}
      </pre>
    </div>
  );
}

function formatPreview(output) {
  if (Array.isArray(output)) {
    return `[${output.slice(0, 2).map(String).join(", ")}${output.length > 2 ? ", ..." : ""}]`;
  }

  if (output && typeof output === "object") {
    const keys = Object.keys(output).slice(0, 3);
    return keys.length ? `{ ${keys.join(", ")} }` : "{}";
  }

  if (typeof output === "boolean") {
    return String(output);
  }

  if (output === null || output === undefined || output === "") {
    return "No output";
  }

  return String(output);
}
