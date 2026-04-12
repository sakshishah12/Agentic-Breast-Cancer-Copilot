export default function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-[#e5e5e5]/90 bg-[#f7f7f7]/90 backdrop-blur-xl">
      <nav className="mx-auto flex w-full max-w-[1520px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-lg bg-[#202020] text-sm font-semibold text-white">
            SS
          </div>
          <div>
            <p className="text-base font-semibold leading-5 text-[#202020]">Sakshi Shah</p>
            <p className="text-sm leading-5 text-[#737373]">Agentic AI Systems | ML Engineer</p>
          </div>
        </div>
        <p className="hidden rounded-lg border border-[#d4d4d4] bg-white px-4 py-2 text-sm font-medium text-[#333333] shadow-sm sm:block">
          Screening dashboard
        </p>
      </nav>
    </header>
  );
}

