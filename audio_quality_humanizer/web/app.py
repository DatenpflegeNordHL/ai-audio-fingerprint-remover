"""FastAPI application for the optional private web backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from audio_quality_humanizer.web.auth import require_bearer_token
from audio_quality_humanizer.web.config import WebConfig, load_config
from audio_quality_humanizer.web.models import SUPPORTED_MODES, health_response, job_response
from audio_quality_humanizer.web.storage import (
    artifact_path,
    cleanup_expired_jobs,
    create_job_directory,
    delete_job,
    get_job_directory,
    input_path_for,
    read_status,
    utc_now_iso,
    write_status,
)
from audio_quality_humanizer.web.upload_validation import copy_upload_to_disk, validate_extension


SAFETY_NOTE = "Private beta technical audio-quality API. Processing execution is deferred in this skeleton."


def create_app() -> FastAPI:
    web_app = FastAPI(
        title="audio-quality-humanizer private web backend",
        version="0.13.0",
        docs_url=None,
        redoc_url=None,
    )

    @web_app.get("/health")
    def health() -> dict:
        return health_response()

    @web_app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
    async def create_job(
        mode: str = Form(...),
        file: UploadFile = File(...),
        config: WebConfig = Depends(require_bearer_token),
    ) -> dict:
        if mode not in SUPPORTED_MODES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported mode for single-file MVP.")
        extension = validate_extension(file.filename)
        job_dir = create_job_directory(config)
        input_path = input_path_for(job_dir, extension)
        input_info = await copy_upload_to_disk(file, input_path, config.max_upload_bytes)
        status_data = {
            "job_id": job_dir.name,
            "status": "uploaded",
            "mode": mode,
            "created_at": utc_now_iso(),
            "input": input_info,
            "processing": {
                "execution": "deferred",
                "message": "Upload accepted and stored for a later safe processing milestone.",
            },
            "artifacts": ["status.json"],
            "safety_notes": [SAFETY_NOTE],
        }
        write_status(job_dir, status_data)
        return job_response(status_data)

    @web_app.get("/api/jobs/{job_id}")
    def get_job(job_id: str, config: WebConfig = Depends(require_bearer_token)) -> dict:
        job_dir = get_job_directory(config, job_id)
        return job_response(read_status(job_dir))

    @web_app.get("/api/jobs/{job_id}/artifacts/{artifact_name:path}")
    def get_artifact(job_id: str, artifact_name: str, config: WebConfig = Depends(require_bearer_token)) -> FileResponse:
        job_dir = get_job_directory(config, job_id)
        path = artifact_path(job_dir, artifact_name)
        if not path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found.")
        return FileResponse(path, media_type=_media_type_for(path), filename=path.name)

    @web_app.delete("/api/jobs/{job_id}")
    def remove_job(job_id: str, config: WebConfig = Depends(require_bearer_token)) -> dict:
        delete_job(config, job_id)
        return {"job_id": job_id, "deleted": True}

    @web_app.post("/api/maintenance/cleanup")
    def cleanup(config: WebConfig = Depends(require_bearer_token)) -> dict:
        removed = cleanup_expired_jobs(config)
        return {"removed_job_ids": removed, "removed_count": len(removed)}

    return web_app


def _media_type_for(path: Path) -> str:
    if path.suffix.casefold() == ".json":
        return "application/json"
    return "application/octet-stream"


app = create_app()
