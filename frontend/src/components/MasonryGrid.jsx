import PatientCard from "./PatientCard.jsx";

export default function MasonryGrid({ analyses, isLoading, onSelect, hasAnyAnalyses }) {
  if (isLoading && !hasAnyAnalyses) {
    return <SkeletonGrid />;
  }

  if (!analyses.length) {
    return (
      <div className="grid min-h-72 place-items-center rounded-lg border border-dashed border-[#d4d4d4] bg-white px-6 py-12 text-center shadow-card">
        <div className="max-w-md">
          <p className="text-xl font-semibold text-[#202020]">
            {hasAnyAnalyses ? "No matching patients" : "No patient analyses yet"}
          </p>
          <p className="mt-2 text-sm leading-6 text-[#666666]">
            {hasAnyAnalyses
              ? "Adjust the filter or search terms to bring cases back into view."
              : "Run the first analysis to start building the screening board."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="masonry-grid">
      {isLoading ? <SkeletonCard /> : null}
      {analyses.map((analysis) => (
        <PatientCard key={analysis.id} analysis={analysis} onSelect={() => onSelect(analysis)} />
      ))}
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="masonry-grid">
      {Array.from({ length: 6 }).map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="mb-4 break-inside-avoid rounded-lg border border-[#e5e5e5] bg-white p-5 shadow-card">
      <div className="h-5 w-24 animate-pulse rounded-lg bg-[#e8e8e8]" />
      <div className="mt-4 h-12 animate-pulse rounded-lg bg-[#e8e8e8]" />
      <div className="mt-3 h-4 w-4/5 animate-pulse rounded-lg bg-[#e8e8e8]" />
      <div className="mt-2 h-4 w-2/3 animate-pulse rounded-lg bg-[#e8e8e8]" />
      <div className="mt-5 h-10 animate-pulse rounded-lg bg-[#e8e8e8]" />
    </div>
  );
}
