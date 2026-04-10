const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface AnalysisResult {
  repo_id: string;
  status: "pending" | "running" | "completed" | "failed";
  repo_name: string;
  repo_url: string;
  total_files: number;
  main_language?: string;
  summary?: string;
  modules: Module[];
  reading_path: ReadingStep[];
  entry_points: string[];
  progress_message?: string;
}

export interface Module {
  name: string;
  path: string;
  description: string;
  files: string[];
  connections: string[];
}

export interface ReadingStep {
  order: number;
  file_path: string;
  reason: string;
  key_concepts: string[];
  estimated_minutes?: number;
}

export async function startAnalysis(githubUrl: string): Promise<{ repo_id: string }> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ github_url: githubUrl }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAnalysis(repoId: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze/${repoId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function sendChatMessage(repoUrl: string, question: string): Promise<{ answer: string }> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, question }),
  });
  if (!res.ok) throw new Error(await res.text());
  // Backend trả về streaming JSON — đọc toàn bộ text rồi parse
  const text = await res.text();
  return JSON.parse(text);
}
