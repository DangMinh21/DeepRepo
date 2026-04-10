from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import concurrent.futures
import json
from app.models.repo import RepoAnalysisRequest, AnalysisStatus
from app.services.analysis_service import run_analysis_pipeline, get_analysis, get_repo_id
from app.agents.qa_agent import answer_question
from app.tools.github_tools import parse_github_url
from pydantic import BaseModel

_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    repo_url: str


@router.post("/analyze")
async def start_analysis(request: RepoAnalysisRequest, background_tasks: BackgroundTasks):
    """Trigger phân tích repo. Trả về repo_id để poll kết quả."""
    repo_id = get_repo_id(request.github_url)

    # Chạy pipeline trong background
    background_tasks.add_task(run_analysis_pipeline, request.github_url)

    return {"repo_id": repo_id, "status": "started"}


@router.get("/analyze/{repo_id}")
async def get_analysis_result(repo_id: str):
    """Lấy kết quả phân tích. Poll endpoint này mỗi 2-3 giây."""
    result = get_analysis(repo_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found. Please start analysis first.")
    return result


@router.get("/analyze/{repo_id}/stream")
async def stream_analysis(repo_id: str):
    """SSE stream cho progress updates."""
    async def event_generator():
        max_wait = 120  # 2 phút timeout
        elapsed = 0
        while elapsed < max_wait:
            result = get_analysis(repo_id)
            if result:
                data = json.dumps(result, ensure_ascii=False)
                yield f"data: {data}\n\n"

                if result.get("status") in [AnalysisStatus.completed, AnalysisStatus.failed]:
                    break
            else:
                yield f"data: {json.dumps({'status': 'pending', 'progress_message': 'Waiting...'})}\n\n"

            await asyncio.sleep(2)
            elapsed += 2

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Hỏi đáp về repo.
    Chạy QA agent trong thread pool để không block event loop,
    trả về SSE stream để tránh timeout trên Render free tier.
    """
    parsed = parse_github_url(request.repo_url)
    if not parsed:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    repo_id = get_repo_id(request.repo_url)
    analysis_context = get_analysis(repo_id)

    async def stream_answer():
        loop = asyncio.get_event_loop()
        # Chạy blocking agent trong thread pool — không block event loop
        answer = await loop.run_in_executor(
            _thread_pool,
            lambda: answer_question(
                owner=parsed["owner"],
                repo_name=parsed["repo_name"],
                question=request.question,
                analysis_context=analysis_context
            )
        )
        yield json.dumps({"answer": answer}, ensure_ascii=False)

    return StreamingResponse(stream_answer(), media_type="application/json")


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "DeepRepo API"}
