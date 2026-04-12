const filters = ["all", "low", "medium", "high"];

export default function FilterBar({ query, onQueryChange, urgencyFilter, onUrgencyChange }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-[#e5e5e5] bg-white p-3 shadow-card md:flex-row md:items-center md:justify-between">
      <input
        type="search"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        className="min-h-11 min-w-0 flex-1 rounded-lg border border-[#d4d4d4] bg-[#fafafa] px-4 text-sm text-[#202020] focus:border-teal-600"
        placeholder="Search symptoms, recommendations, or reasoning"
      />

      <div className="flex flex-wrap gap-2">
        {filters.map((filter) => (
          <button
            key={filter}
            type="button"
            onClick={() => onUrgencyChange(filter)}
            className={`min-h-11 rounded-lg px-4 text-sm font-semibold capitalize transition ${
              urgencyFilter === filter
                ? "bg-[#202020] text-white"
                : "border border-[#d4d4d4] bg-[#fafafa] text-[#4b4b4b] hover:border-teal-500"
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </div>
  );
}
