"""FastAPI application for the optional private web backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse

from audio_quality_humanizer.web.auth import require_bearer_token
from audio_quality_humanizer.web.config import WebConfig
from audio_quality_humanizer.web.models import SUPPORTED_MODES, health_response, job_response
from audio_quality_humanizer.web.processing import execute_job
from audio_quality_humanizer.web.storage import (
    artifact_path,
    cleanup_expired_jobs,
    create_job_directory,
    delete_job,
    get_job_directory,
    input_path_for,
    read_status,
    write_status,
    utc_now_iso,
)
from audio_quality_humanizer.web.upload_validation import copy_upload_to_disk, validate_extension


SAFETY_NOTE = (
    "Private beta technical audio-quality API. Reports show measured technical audio features only."
)


def create_app() -> FastAPI:
    web_app = FastAPI(
        title="audio-quality-humanizer private web backend",
        version="0.13.1",
        docs_url=None,
        redoc_url=None,
    )

    @web_app.get("/", response_class=HTMLResponse)
    def operator_page() -> str:
        return _operator_page_html()

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
                "execution": "pending",
                "message": "Upload accepted. Safe single-file processing will run synchronously.",
            },
            "artifacts": ["status.json"],
            "safety_notes": [SAFETY_NOTE],
        }
        write_status(job_dir, status_data)
        status_data = execute_job(job_dir, input_path, mode)
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


def _operator_page_html() -> str:
    modes = "".join(f'<option value="{mode}">{mode}</option>' for mode in SUPPORTED_MODES)
    supported = "".join(f"<li>{mode}</li>" for mode in SUPPORTED_MODES)
    deferred = "".join(f"<li>{mode}</li>" for mode in ("clean-metadata", "humanize", "compare", "visualize-compare"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Audio Quality Humanizer Private Backend</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #0d1117; color: #e6edf3; }}
    main {{ width: min(1080px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0; }}
    header {{ border-bottom: 1px solid #30363d; padding-bottom: 20px; margin-bottom: 24px; }}
    h1 {{ font-size: 30px; margin: 0 0 10px; font-weight: 750; }}
    h2 {{ font-size: 18px; margin: 0 0 12px; }}
    p {{ color: #9da7b1; line-height: 1.55; }}
    .grid {{ display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr); gap: 18px; }}
    section {{ border: 1px solid #30363d; background: #161b22; border-radius: 8px; padding: 18px; }}
    label {{ display: block; color: #c9d1d9; font-size: 14px; margin: 14px 0 6px; }}
    input, select, button {{ box-sizing: border-box; width: 100%; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: #e6edf3; padding: 10px 12px; font: inherit; }}
    input[type=file] {{ padding: 9px; }}
    button {{ margin-top: 16px; background: #238636; border-color: #2ea043; cursor: pointer; font-weight: 700; }}
    button:disabled {{ opacity: 0.65; cursor: wait; }}
    ul {{ padding-left: 20px; color: #c9d1d9; }}
    pre {{ min-height: 150px; white-space: pre-wrap; word-break: break-word; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 12px; color: #c9d1d9; }}
    .status {{ display: inline-flex; align-items: center; border: 1px solid #2ea043; color: #7ee787; border-radius: 999px; padding: 4px 10px; font-size: 13px; }}
    .links a {{ display: block; color: #58a6ff; margin: 8px 0; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ width: min(100% - 20px, 1080px); padding-top: 20px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="status">Private beta backend</div>
      <h1>Audio Quality Humanizer Private Backend</h1>
      <p>Upload one local audio file, run a safe single-file technical mode, and download generated JSON artifacts. This local page uses no external JavaScript, CSS, cookies, or persistent browser storage.</p>
    </header>
    <div class="grid">
      <section>
        <h2>Upload Job</h2>
        <form id="job-form">
          <label for="token">Bearer token</label>
          <input id="token" name="token" type="password" autocomplete="off" required>
          <label for="mode">Mode</label>
          <select id="mode" name="mode">{modes}</select>
          <label for="file">Audio file</label>
          <input id="file" name="file" type="file" accept=".wav,.flac,.mp3,.m4a,.aac,.ogg,.opus,.aif,.aiff" required>
          <button id="submit" type="submit">Create job</button>
        </form>
      </section>
      <section>
        <h2>Modes</h2>
        <p>Supported now</p>
        <ul>{supported}</ul>
        <p>Deferred</p>
        <ul>{deferred}</ul>
      </section>
    </div>
    <section style="margin-top:18px">
      <h2>Job Result</h2>
      <pre id="result">No job submitted yet.</pre>
      <div id="artifacts" class="links"></div>
    </section>
    <section style="margin-top:18px">
      <h2>Safety Note</h2>
      <p>Reports show measured technical audio features only. They are not mastering certification and do not predict platform or distributor acceptance.</p>
    </section>
  </main>
  <script>
    const form = document.getElementById('job-form');
    const result = document.getElementById('result');
    const artifacts = document.getElementById('artifacts');
    const submit = document.getElementById('submit');
    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      artifacts.textContent = '';
      submit.disabled = true;
      result.textContent = 'Creating job...';
      const token = document.getElementById('token').value;
      const data = new FormData();
      data.append('mode', document.getElementById('mode').value);
      data.append('file', document.getElementById('file').files[0]);
      try {{
        const response = await fetch('/api/jobs', {{
          method: 'POST',
          headers: {{ Authorization: `Bearer ${{token}}` }},
          body: data
        }});
        const payload = await response.json();
        result.textContent = JSON.stringify(payload, null, 2);
        if (response.ok && payload.job_id && Array.isArray(payload.artifacts)) {{
          for (const name of payload.artifacts) {{
            const link = document.createElement('a');
            const url = `/api/jobs/${{payload.job_id}}/artifacts/${{encodeURIComponent(name)}}`;
            link.href = url;
            link.textContent = `Download ${{name}}`;
            link.addEventListener('click', async (clickEvent) => {{
              clickEvent.preventDefault();
              const artifactResponse = await fetch(url, {{
                headers: {{ Authorization: `Bearer ${{document.getElementById('token').value}}` }}
              }});
              if (!artifactResponse.ok) {{
                result.textContent = 'Artifact download failed safely.';
                return;
              }}
              const blob = await artifactResponse.blob();
              const objectUrl = URL.createObjectURL(blob);
              const download = document.createElement('a');
              download.href = objectUrl;
              download.download = name;
              document.body.appendChild(download);
              download.click();
              download.remove();
              URL.revokeObjectURL(objectUrl);
            }});
            artifacts.appendChild(link);
          }}
        }}
      }} catch (error) {{
        result.textContent = 'Request failed safely.';
      }} finally {{
        submit.disabled = false;
      }}
    }});
  </script>
</body>
</html>"""


app = create_app()
