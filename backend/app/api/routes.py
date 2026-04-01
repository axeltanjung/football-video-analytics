from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import UPLOAD_DIR, OUTPUT_DIR
from app.database import get_db
from app.models.match import Match, MatchStatus
from app.pipeline.pipeline import MatchPipeline
from app.api.websocket import manager

logger = logging.getLogger(__name__)
router = APIRouter()


async def _update_progress(match_id: str, status: str, progress: float):
    await manager.broadcast(match_id, {
        "type": "progress",
        "match_id": match_id,
        "status": status,
        "progress": round(progress, 1),
    })


async def _run_pipeline(match_id: str, video_path: str, db_url: str):
    from app.database import async_session

    async with async_session() as session:
        try:
            stmt = select(Match).where(Match.id == match_id)
            result = await session.execute(stmt)
            match = result.scalar_one_or_none()
            if not match:
                return

            match.status = MatchStatus.PROCESSING
            await session.commit()

            await _update_progress(match_id, "processing", 0)

            pipeline = MatchPipeline(
                match_id=match_id,
                video_path=video_path,
                progress_callback=_update_progress,
            )

            analytics = await pipeline.run()

            match.status = MatchStatus.COMPLETED
            match.analytics_json = analytics.to_dict()
            match.events_json = [
                {
                    "event_type": e.event_type,
                    "timestamp": round(e.timestamp, 2),
                    "player_id": e.player_id,
                    "team_id": e.team_id,
                    "position": e.position,
                    "metadata": e.metadata,
                }
                for e in analytics.events
            ]
            match.duration_seconds = analytics.duration_seconds
            match.progress = 100.0

            heatmap_path = OUTPUT_DIR / f"{match_id}_heatmap.png"
            if heatmap_path.exists():
                match.heatmap_path = str(heatmap_path)

            await session.commit()
            await _update_progress(match_id, "completed", 100)

        except Exception as e:
            logger.exception(f"Pipeline failed for match {match_id}")
            match.status = MatchStatus.FAILED
            match.error_message = str(e)
            await session.commit()
            await _update_progress(match_id, "failed", 0)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
        raise HTTPException(400, f"Unsupported format: {ext}")

    match_id = str(uuid.uuid4())
    saved_name = f"{match_id}{ext}"
    save_path = UPLOAD_DIR / saved_name

    async with aiofiles.open(save_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)

    match = Match(
        id=match_id,
        filename=saved_name,
        original_filename=file.filename,
        status=MatchStatus.UPLOADED,
    )

    try:
        import cv2
        cap = cv2.VideoCapture(str(save_path))
        if cap.isOpened():
            match.fps = cap.get(cv2.CAP_PROP_FPS)
            match.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            match.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            match.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            match.duration_seconds = match.total_frames / max(match.fps, 1)
            cap.release()
    except Exception:
        pass

    db.add(match)
    await db.commit()

    return {
        "match_id": match_id,
        "status": "uploaded",
        "filename": file.filename,
        "message": "Video uploaded. POST /api/process/{match_id} to start analysis.",
    }


@router.post("/process/{match_id}")
async def process_match(
    match_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(404, "Match not found")

    if match.status == MatchStatus.PROCESSING:
        raise HTTPException(409, "Already processing")

    video_path = str(UPLOAD_DIR / match.filename)
    if not Path(video_path).exists():
        raise HTTPException(404, "Video file not found")

    match.status = MatchStatus.PROCESSING
    match.progress = 0.0
    await db.commit()

    from app.config import DATABASE_URL
    background_tasks.add_task(_run_pipeline, match_id, video_path, DATABASE_URL)

    return {"match_id": match_id, "status": "processing"}


@router.get("/results/{match_id}")
async def get_results(match_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(404, "Match not found")

    return {
        "match_id": match.id,
        "status": match.status,
        "filename": match.original_filename,
        "progress": match.progress,
        "duration_seconds": match.duration_seconds,
        "analytics": match.analytics_json,
        "events": match.events_json,
        "heatmap_url": f"/outputs/{match_id}_heatmap.png" if match.heatmap_path else None,
    }


@router.get("/metrics/{match_id}")
async def get_metrics(match_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(404, "Match not found")

    if match.status != MatchStatus.COMPLETED:
        return {"match_id": match_id, "status": match.status, "metrics": None}

    analytics = match.analytics_json or {}

    return {
        "match_id": match_id,
        "possession": analytics.get("possession", {}),
        "possession_timeline": analytics.get("possession_timeline", []),
        "passes": analytics.get("total_passes", {}),
        "pass_accuracy": analytics.get("pass_accuracy", {}),
        "shots": analytics.get("shots", {}),
        "shots_on_target": analytics.get("shots_on_target", {}),
        "duration_seconds": analytics.get("duration_seconds", 0),
        "total_frames": analytics.get("total_frames_processed", 0),
    }


@router.get("/matches")
async def list_matches(db: AsyncSession = Depends(get_db)):
    stmt = select(Match).order_by(Match.created_at.desc())
    result = await db.execute(stmt)
    matches = result.scalars().all()

    return [
        {
            "match_id": m.id,
            "filename": m.original_filename,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "progress": m.progress,
            "duration_seconds": m.duration_seconds,
        }
        for m in matches
    ]


@router.get("/heatmap/{match_id}")
async def get_heatmap(match_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()

    if not match or not match.heatmap_path:
        raise HTTPException(404, "Heatmap not available")

    return FileResponse(match.heatmap_path, media_type="image/png")
