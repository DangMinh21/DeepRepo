"use client";
import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { getAnalysis, type AnalysisResult } from "@/lib/api";
import ArchitectureView from "@/components/ArchitectureView";
import ReadingPathView from "@/components/ReadingPathView";
import ChatPanel from "@/components/ChatPanel";

type Tab = "architecture" | "reading" | "chat";

export default function AnalyzePage() {
  const { id } = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const repoUrl = searchParams.get("url") || "";

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [tab, setTab] = useState<Tab>("architecture");
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!id) return;
    const poll = async () => {
      try {
        const data = await getAnalysis(id);
        setResult(data);
        if (data.status === "completed" || data.status === "failed") {
          setPolling(false);
        }
      } catch {
        // retry silently
      }
    };
    poll();
    if (!polling) return;
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [id, polling]);

  const isLoading = !result || result.status === "pending" || result.status === "running";

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
        <a href="/" className="font-bold text-lg">
          Deep<span className="text-emerald-400">Repo</span>
        </a>
        {result && (
          <span className="text-zinc-400 text-sm font-mono">{result.repo_name}</span>
        )}
      </header>

      {/* Loading state */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
          <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-zinc-400 text-sm">
            {result?.progress_message || "Initializing AI agents..."}
          </p>
          <p className="text-zinc-600 text-xs">This usually takes 30–60 seconds</p>
        </div>
      )}

      {/* Failed state */}
      {result?.status === "failed" && (
        <div className="flex flex-col items-center justify-center h-[80vh] space-y-4">
          <p className="text-red-400 text-lg">Analysis failed</p>
          <p className="text-zinc-500 text-sm">{result.progress_message}</p>
          <a href="/" className="text-emerald-400 hover:underline text-sm">Try another repo</a>
        </div>
      )}

      {/* Completed state */}
      {result?.status === "completed" && (
        <div className="flex flex-col h-[calc(100vh-65px)]">
          {/* Summary bar */}
          <div className="px-6 py-3 bg-zinc-900 border-b border-zinc-800 flex items-center gap-6 text-sm">
            {result.main_language && (
              <span className="text-zinc-400">
                <span className="text-white font-medium">{String(result.main_language)}</span>
              </span>
            )}
            <span className="text-zinc-400">
              <span className="text-white font-medium">{result.modules?.length ?? 0}</span> modules
            </span>
            <span className="text-zinc-400">
              <span className="text-white font-medium">{result.reading_path?.length ?? 0}</span> reading steps
            </span>
          </div>

          {/* Tab navigation */}
          <nav className="flex gap-1 px-6 pt-4 border-b border-zinc-800">
            {(["architecture", "reading", "chat"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors capitalize cursor-pointer ${
                  tab === t
                    ? "bg-zinc-800 text-white border border-b-0 border-zinc-700"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {t === "architecture" ? "🗺️ Architecture" : t === "reading" ? "📚 Reading Path" : "💬 Chat"}
              </button>
            ))}
          </nav>

          {/* Tab content */}
          <div className="flex-1 overflow-auto p-6">
            {tab === "architecture" && <ArchitectureView modules={result.modules ?? []} summary={result.summary} entryPoints={result.entry_points ?? []} />}
            {tab === "reading" && <ReadingPathView steps={result.reading_path ?? []} />}
            {tab === "chat" && <ChatPanel repoUrl={repoUrl} />}
          </div>
        </div>
      )}
    </div>
  );
}
