from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AnalysisStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class RepoAnalysisRequest(BaseModel):
    github_url: str
    branch: Optional[str] = "main"


class FileNode(BaseModel):
    path: str
    type: str  # "file" | "dir"
    size: Optional[int] = None
    language: Optional[str] = None


class ArchitectureModule(BaseModel):
    name: str
    path: str
    description: str
    files: list[str]
    connections: list[str]  # tên module khác mà module này phụ thuộc vào


class ReadingStep(BaseModel):
    order: int
    file_path: str
    reason: str
    key_concepts: list[str]


class AnalysisResult(BaseModel):
    repo_id: str
    status: AnalysisStatus
    repo_name: str
    repo_url: str
    total_files: int
    main_language: Optional[str] = None
    summary: Optional[str] = None
    modules: list[ArchitectureModule] = []
    reading_path: list[ReadingStep] = []
    entry_points: list[str] = []
    progress_message: Optional[str] = None
