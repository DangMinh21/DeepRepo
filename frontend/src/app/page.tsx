"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { startAnalysis } from "@/lib/api";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const { repo_id } = await startAnalysis(url.trim());
      router.push(`/analyze/${repo_id}?url=${encodeURIComponent(url.trim())}`);
    } catch {
      setError("Failed to start analysis. Check the URL and try again.");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Badge */}
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 bg-zinc-800 border border-zinc-700 rounded-full px-4 py-1.5 text-sm text-zinc-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Agentic AI · Powered by Claude
          </div>
          <h1 className="text-5xl font-bold tracking-tight">
            Deep<span className="text-emerald-400">Repo</span>
          </h1>
          <p className="text-xl text-zinc-400">
            Paste any GitHub repo. Get a complete learning map in minutes.
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 transition-colors"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-white font-semibold px-6 py-3 rounded-lg transition-colors whitespace-nowrap cursor-pointer"
            >
              {loading ? "Starting..." : "Analyze Repo"}
            </button>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </form>

        {/* Example repos */}
        <div className="space-y-2">
          <p className="text-zinc-500 text-sm">Try an example:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {["fastapi/fastapi", "vercel/next.js", "anthropics/anthropic-sdk-python"].map((repo) => (
              <button
                key={repo}
                onClick={() => setUrl(`https://github.com/${repo}`)}
                className="text-xs bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 px-3 py-1.5 rounded-full transition-colors cursor-pointer"
              >
                {repo}
              </button>
            ))}
          </div>
        </div>

        {/* Feature cards */}
        <div className="grid grid-cols-3 gap-4 pt-4">
          {[
            { icon: "🗺️", title: "Architecture Map", desc: "Understand module structure visually" },
            { icon: "📚", title: "Reading Path", desc: "AI-guided file reading order" },
            { icon: "💬", title: "Code Q&A", desc: "Ask anything about the codebase" },
          ].map((f) => (
            <div key={f.title} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-left">
              <div className="text-2xl mb-2">{f.icon}</div>
              <div className="font-semibold text-sm">{f.title}</div>
              <div className="text-zinc-500 text-xs mt-1">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
