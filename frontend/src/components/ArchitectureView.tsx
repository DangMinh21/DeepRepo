import type { Module } from "@/lib/api";

interface Props {
  modules: Module[];
  summary?: string;
  entryPoints: string[];
}

export default function ArchitectureView({ modules, summary, entryPoints }: Props) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Summary */}
      {summary && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-2">Overview</h2>
          <p className="text-zinc-200 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Entry Points */}
      {entryPoints.length > 0 && (
        <div className="bg-zinc-900 border border-emerald-900/50 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3">Entry Points</h2>
          <div className="flex flex-wrap gap-2">
            {entryPoints.map((ep) => (
              <span key={ep} className="font-mono text-xs bg-zinc-800 border border-zinc-700 text-emerald-300 px-3 py-1.5 rounded-lg">
                {ep}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Modules */}
      <div>
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-3">Modules</h2>
        <div className="grid gap-3">
          {modules.map((mod) => (
            <div key={mod.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-white">{mod.name}</h3>
                  <p className="text-zinc-500 text-xs font-mono mt-0.5">{mod.path}</p>
                </div>
                {mod.connections.length > 0 && (
                  <div className="flex flex-wrap gap-1 justify-end">
                    {mod.connections.map((c) => (
                      <span key={c} className="text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full border border-zinc-700">
                        → {c}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <p className="text-zinc-300 text-sm">{mod.description}</p>
              {mod.files.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {mod.files.map((f) => (
                    <span key={f} className="font-mono text-xs text-zinc-500 bg-zinc-800/50 px-2 py-0.5 rounded">
                      {f}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
