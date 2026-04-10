import type { ReadingStep } from "@/lib/api";

interface Props {
  steps: ReadingStep[];
}

export default function ReadingPathView({ steps }: Props) {
  if (steps.length === 0) {
    return <p className="text-zinc-500 text-center mt-10">No reading path generated yet.</p>;
  }

  const totalMinutes = steps.reduce((acc, s) => acc + (s.estimated_minutes || 10), 0);

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-semibold text-zinc-200">
          {steps.length} files · ~{Math.round(totalMinutes / 60 * 10) / 10}h estimated
        </h2>
        <span className="text-xs text-zinc-500">Read in this order for best understanding</span>
      </div>

      {steps.map((step, idx) => (
        <div key={step.file_path} className="flex gap-4">
          {/* Step number + connector line */}
          <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
              idx === 0 ? "bg-emerald-500 text-white" : "bg-zinc-800 text-zinc-400 border border-zinc-700"
            }`}>
              {step.order}
            </div>
            {idx < steps.length - 1 && (
              <div className="w-px flex-1 bg-zinc-800 my-1" />
            )}
          </div>

          {/* Content */}
          <div className="pb-4 flex-1">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <code className="text-sm text-emerald-300 font-mono">{step.file_path}</code>
                {step.estimated_minutes && (
                  <span className="text-xs text-zinc-500 flex-shrink-0">{step.estimated_minutes} min</span>
                )}
              </div>
              <p className="text-zinc-300 text-sm">{step.reason}</p>
              {step.key_concepts.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {step.key_concepts.map((c) => (
                    <span key={c} className="text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full border border-zinc-700">
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
