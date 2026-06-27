"""FastAPI application for the optional private web backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse

from audio_quality_humanizer.web.auth import require_bearer_token, require_beta_dashboard_access
from audio_quality_humanizer.web.config import WebConfig
from audio_quality_humanizer.__version__ import __version__
from audio_quality_humanizer.web.models import SINGLE_FILE_MODES, SUPPORTED_MODES, TWO_FILE_MODES, health_response, job_response
from audio_quality_humanizer.web.processing import execute_job, execute_two_file_job, execute_workflow_job
from audio_quality_humanizer.web.storage import (
    active_job_count,
    artifact_path,
    cleanup_expired_jobs,
    create_job_directory,
    delete_job,
    get_job_directory,
    input_path_for,
    list_job_summaries,
    named_input_path_for,
    read_status,
    write_status,
    utc_now_iso,
)
from audio_quality_humanizer.web.upload_validation import copy_upload_to_disk, validate_extension
from audio_quality_humanizer.web.workflow_registry import WORKFLOW_DEFINITIONS, WORKFLOW_NAMES, workflow_config, workflow_status_steps


SAFETY_NOTE = (
    "Private beta technical audio-quality API. Reports show measured technical audio features only."
)


def create_app() -> FastAPI:
    web_app = FastAPI(
        title="audio-quality-humanizer private web backend",
        version=__version__,
        docs_url=None,
        redoc_url=None,
    )

    @web_app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @web_app.get("/", response_class=HTMLResponse)
    def operator_page(_config: WebConfig = Depends(require_beta_dashboard_access)) -> str:
        return _operator_page_html()

    @web_app.get("/health")
    def health() -> dict:
        return health_response()

    @web_app.get("/api/config")
    def get_safe_config(config: WebConfig = Depends(require_bearer_token)) -> dict:
        return {
            "private_beta": True,
            "web_host": config.host,
            "web_port": config.port,
            "max_upload_mib": config.max_upload_mib,
            "job_ttl_hours": config.job_ttl_hours,
            "partial_ttl_minutes": config.partial_ttl_minutes,
            "max_active_jobs": config.max_active_jobs,
            "supported_modes": list(SUPPORTED_MODES),
            "single_file_modes": list(SINGLE_FILE_MODES),
            "two_file_modes": list(TWO_FILE_MODES),
            "deferred_modes": ["humanize"],
            "workflow_modes": list(WORKFLOW_NAMES),
            "workflows": workflow_config(),
        }

    @web_app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
    async def create_job(
        mode: str = Form(...),
        file: UploadFile = File(...),
        config: WebConfig = Depends(require_bearer_token),
    ) -> dict:
        if mode not in SINGLE_FILE_MODES and mode not in WORKFLOW_NAMES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported mode for single-file MVP.")
        _enforce_active_job_limit(config)
        extension = validate_extension(file.filename)
        job_dir = create_job_directory(config)
        input_path = input_path_for(job_dir, extension)
        input_info = await copy_upload_to_disk(file, input_path, config.max_upload_bytes)
        status_data = {
            "job_id": job_dir.name,
            "status": "uploaded",
            "mode": "workflow" if mode in WORKFLOW_NAMES else mode,
            "created_at": utc_now_iso(),
            "input": input_info,
            "processing": {
                "execution": "pending",
                "message": "Upload accepted. Safe processing will run synchronously.",
            },
            "artifacts": ["status.json"],
            "safety_notes": [SAFETY_NOTE],
        }
        if mode in WORKFLOW_NAMES:
            status_data["workflow_name"] = mode
            status_data["workflow_label"] = WORKFLOW_DEFINITIONS[mode]["label"]
            status_data["steps"] = workflow_status_steps(mode)
            status_data["artifact_groups"] = {}
        write_status(job_dir, status_data)
        if mode in WORKFLOW_NAMES:
            status_data = execute_workflow_job(job_dir, input_path, mode)
        else:
            status_data = execute_job(job_dir, input_path, mode)
        return job_response(status_data)

    @web_app.post("/api/compare-jobs", status_code=status.HTTP_201_CREATED)
    async def create_compare_job(
        mode: str = Form(...),
        before_file: UploadFile = File(...),
        after_file: UploadFile = File(...),
        config: WebConfig = Depends(require_bearer_token),
    ) -> dict:
        if mode not in TWO_FILE_MODES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported mode for two-file MVP.")
        _enforce_active_job_limit(config)
        before_extension = validate_extension(before_file.filename)
        after_extension = validate_extension(after_file.filename)
        job_dir = create_job_directory(config)
        before_path = named_input_path_for(job_dir, "before", before_extension)
        after_path = named_input_path_for(job_dir, "after", after_extension)
        before_info = await copy_upload_to_disk(before_file, before_path, config.max_upload_bytes)
        after_info = await copy_upload_to_disk(after_file, after_path, config.max_upload_bytes)
        status_data = {
            "job_id": job_dir.name,
            "status": "uploaded",
            "mode": mode,
            "created_at": utc_now_iso(),
            "inputs": {"before": before_info, "after": after_info},
            "processing": {
                "execution": "pending",
                "message": "Uploads accepted. Safe two-file processing will run synchronously.",
            },
            "artifacts": ["status.json"],
            "safety_notes": [SAFETY_NOTE],
        }
        write_status(job_dir, status_data)
        status_data = execute_two_file_job(job_dir, before_path, after_path, mode)
        return job_response(status_data)

    @web_app.get("/api/jobs")
    def list_jobs(config: WebConfig = Depends(require_bearer_token)) -> dict:
        jobs = list_job_summaries(config)
        return {"jobs": jobs, "count": len(jobs)}

    @web_app.get("/api/jobs/{job_id}")
    def get_job(job_id: str, config: WebConfig = Depends(require_bearer_token)) -> dict:
        job_dir = get_job_directory(config, job_id)
        return job_response(read_status(job_dir))

    @web_app.get("/api/jobs/{job_id}/artifacts/{artifact_name:path}")
    def get_artifact(job_id: str, artifact_name: str, config: WebConfig = Depends(require_bearer_token)) -> FileResponse:
        job_dir = get_job_directory(config, job_id)
        path = artifact_path(job_dir, artifact_name)
        status_data = read_status(job_dir)
        if artifact_name not in status_data.get("artifacts", []):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found.")
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


def _enforce_active_job_limit(config: WebConfig) -> None:
    if active_job_count(config) >= config.max_active_jobs:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Private beta active job limit reached.",
        )


def _media_type_for(path: Path) -> str:
    if path.suffix.casefold() == ".json":
        return "application/json"
    if path.suffix.casefold() == ".md":
        return "text/markdown; charset=utf-8"
    media_types = {
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".aac": "audio/mp4",
        ".ogg": "audio/ogg",
        ".opus": "audio/ogg",
        ".aif": "audio/aiff",
        ".aiff": "audio/aiff",
    }
    if path.suffix.casefold() in media_types:
        return media_types[path.suffix.casefold()]
    return "application/octet-stream"


def _operator_page_html() -> str:
    single_mode_options = "".join(f'<option value="{mode}">{mode}</option>' for mode in SINGLE_FILE_MODES)
    workflow_options = "".join(
        f'<option value="{name}">{definition["label"]}</option>' for name, definition in WORKFLOW_DEFINITIONS.items()
    )
    two_mode_options = "".join(f'<option value="{mode}">{mode}</option>' for mode in TWO_FILE_MODES)
    modes = (
        f'<optgroup label="Single-file modes">{single_mode_options}</optgroup>'
        f'<optgroup label="Private beta workflows">{workflow_options}</optgroup>'
        f'<optgroup label="Two-file modes">{two_mode_options}</optgroup>'
    )
    single_file_modes = "".join(f"<li>{mode}</li>" for mode in SINGLE_FILE_MODES)
    two_file_modes = "".join(f"<li>{mode}</li>" for mode in TWO_FILE_MODES)
    deferred = "".join(f"<li>{mode}</li>" for mode in ("humanize",))
    workflow_cards = "".join(
        f'<article class="workflow-card"><h3>{definition["label"]}</h3><p>{definition["description"]}</p></article>'
        for definition in WORKFLOW_DEFINITIONS.values()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Audio Quality Humanizer</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #090d13; color: #e6edf3; }}
    main {{ width: min(1220px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0; }}
    header {{ display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; border-bottom: 1px solid #243244; padding-bottom: 20px; margin-bottom: 22px; }}
    h1 {{ font-size: 34px; margin: 0 0 8px; font-weight: 760; }}
    h2 {{ font-size: 17px; margin: 0 0 12px; }}
    h3 {{ font-size: 15px; margin: 0 0 8px; }}
    p {{ color: #9da7b1; line-height: 1.55; }}
    .layout {{ display: grid; grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.6fr); gap: 18px; align-items: start; }}
    .stack {{ display: grid; gap: 18px; }}
    .panel {{ border: 1px solid #243244; background: #111822; border-radius: 8px; padding: 18px; box-shadow: 0 16px 40px rgba(0,0,0,.22); }}
    label {{ display: block; color: #c9d1d9; font-size: 14px; margin: 14px 0 6px; }}
    input, select, button {{ box-sizing: border-box; width: 100%; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: #e6edf3; padding: 10px 12px; font: inherit; }}
    input[type=file] {{ padding: 9px; }}
    button {{ margin-top: 16px; background: #238636; border-color: #2ea043; cursor: pointer; font-weight: 700; }}
    button:disabled {{ opacity: 0.65; cursor: wait; }}
    ul {{ padding-left: 20px; color: #c9d1d9; }}
    pre {{ max-height: 360px; overflow: auto; white-space: pre-wrap; word-break: break-word; background: #0b1017; border: 1px solid #243244; border-radius: 6px; padding: 12px; color: #c9d1d9; }}
    canvas {{ width: 100%; max-width: 100%; height: 170px; border: 1px solid #243244; border-radius: 6px; background: #0b1017; }}
    table {{ width: 100%; border-collapse: collapse; }}
    td, th {{ border-bottom: 1px solid #243244; padding: 8px 4px; text-align: left; vertical-align: top; }}
    .badge {{ display: inline-flex; align-items: center; border: 1px solid #2ea043; color: #7ee787; border-radius: 999px; padding: 4px 10px; font-size: 13px; }}
    .badge.warn {{ border-color: #d29922; color: #f2cc60; }}
    .links button {{ margin: 7px 8px 0 0; width: auto; background: #1f6feb; border-color: #388bfd; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; }}
    .card {{ border: 1px solid #243244; background: #0b1017; border-radius: 8px; padding: 12px; }}
    .card strong {{ display: block; font-size: 20px; margin-top: 6px; }}
    .workflow-grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; }}
    .workflow-card {{ border: 1px solid #243244; background: #0b1017; border-radius: 8px; padding: 12px; }}
    .workflow-card p {{ margin: 0; font-size: 14px; }}
    .step-list {{ display: grid; gap: 8px; margin-top: 12px; }}
    .step {{ display: flex; justify-content: space-between; gap: 10px; border: 1px solid #243244; border-radius: 6px; padding: 8px 10px; background: #0b1017; }}
    .artifact-group {{ margin-top: 12px; }}
    .artifact-group h3 {{ color: #c9d1d9; }}
    .muted {{ color: #9da7b1; }}
    .empty {{ color: #8b949e; font-style: italic; }}
    @media (max-width: 860px) {{ header, .layout {{ grid-template-columns: 1fr; display: grid; }} main {{ width: min(100% - 20px, 1220px); padding-top: 20px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Audio Quality Humanizer</h1>
        <p>Local private dashboard for generated technical audio reports. Real artifact data only; no external JavaScript, CSS, cookies, or persistent browser storage.</p>
      </div>
      <div>
        <div class="badge">Local private beta</div>
        <div class="badge warn">Do not expose directly to the public internet</div>
      </div>
    </header>
    <div class="layout">
      <div class="stack">
        <section class="panel" id="upload-panel">
          <h2>Upload</h2>
          <form id="job-form">
            <label for="token">Bearer token</label>
            <input id="token" name="token" type="password" autocomplete="off" required>
            <label for="mode">Mode</label>
            <select id="mode" name="mode">{modes}</select>
            <div id="single-file-fields">
              <label for="file">Audio file</label>
              <input id="file" name="file" type="file" accept=".wav,.flac,.mp3,.m4a,.aac,.ogg,.opus,.aif,.aiff">
            </div>
            <div id="two-file-fields" hidden>
              <label for="before-file">Before audio file</label>
              <input id="before-file" name="before_file" type="file" accept=".wav,.flac,.mp3,.m4a,.aac,.ogg,.opus,.aif,.aiff">
              <label for="after-file">After audio file</label>
              <input id="after-file" name="after_file" type="file" accept=".wav,.flac,.mp3,.m4a,.aac,.ogg,.opus,.aif,.aiff">
            </div>
            <button id="submit" type="submit">Create job</button>
          </form>
        </section>
        <section class="panel" id="mode-panel">
          <h2>Modes</h2>
          <p class="muted">Single-file modes</p>
          <ul>{single_file_modes}</ul>
          <p class="muted">Two-file modes</p>
          <ul>{two_file_modes}</ul>
          <p class="muted">Private beta workflows</p>
          <div class="workflow-grid">{workflow_cards}</div>
          <p class="muted">Deferred</p>
          <ul>{deferred}</ul>
        </section>
        <section class="panel" id="operator-panel">
          <h2>Operator</h2>
          <div id="config-view" class="cards"><p class="empty">Retention settings appear after refresh.</p></div>
          <button id="refresh-config" type="button">Refresh operator data</button>
          <button id="cleanup-jobs" type="button">Run cleanup</button>
          <pre id="cleanup-result">No cleanup run yet.</pre>
        </section>
        <section class="panel" id="faq-panel">
          <h2>Safety / FAQ</h2>
          <p>This is a local private beta. Reports show measured technical audio features only.</p>
          <p>No platform or distributor acceptance guarantee. No frontend framework, deployment, DNS, or public launch in this milestone.</p>
        </section>
      </div>
      <div class="stack">
        <section class="panel" id="job-status-panel">
          <h2>Job Status</h2>
          <div id="status-fields" class="cards"></div>
          <div id="step-progress" class="step-list"></div>
          <pre id="result">No job submitted yet.</pre>
        </section>
        <section class="panel" id="artifact-panel">
          <h2>Artifacts</h2>
          <div id="artifacts" class="links"></div>
          <button id="preview-all" type="button" disabled>Preview result</button>
        </section>
        <section class="panel" id="recent-jobs-panel">
          <h2>Recent Jobs</h2>
          <div id="recent-jobs"><p class="empty">Recent jobs appear after refresh.</p></div>
        </section>
        <section class="panel" id="metric-panel">
          <h2>Metric Cards</h2>
          <div id="metrics" class="cards"><p class="empty">Metrics appear after an artifact preview.</p></div>
        </section>
        <section class="panel" id="visualization-panel">
          <h2>Visualization Preview</h2>
          <p class="muted">Waveform preview</p>
          <canvas id="waveform" width="900" height="170"></canvas>
          <p class="muted">Spectrogram energy preview</p>
          <canvas id="spectrogram" width="900" height="170"></canvas>
          <p id="visual-empty" class="empty">Visualization artifact data not loaded.</p>
        </section>
        <section class="panel" id="metadata-panel">
          <h2>Metadata</h2>
          <div id="metadata-view"><p class="empty">Metadata artifact data not loaded.</p></div>
        </section>
        <section class="panel" id="raw-json-panel">
          <h2>Raw JSON Preview</h2>
          <pre id="raw-json">No artifact preview loaded.</pre>
        </section>
      </div>
    </div>
  </main>
  <script>
    const form = document.getElementById('job-form');
    const result = document.getElementById('result');
    const artifacts = document.getElementById('artifacts');
    const submit = document.getElementById('submit');
    const previewAll = document.getElementById('preview-all');
    const statusFields = document.getElementById('status-fields');
    const stepProgress = document.getElementById('step-progress');
    const metrics = document.getElementById('metrics');
    const rawJson = document.getElementById('raw-json');
    const metadataView = document.getElementById('metadata-view');
    const visualEmpty = document.getElementById('visual-empty');
    const configView = document.getElementById('config-view');
    const refreshConfig = document.getElementById('refresh-config');
    const cleanupJobs = document.getElementById('cleanup-jobs');
    const cleanupResult = document.getElementById('cleanup-result');
    const recentJobs = document.getElementById('recent-jobs');
    const modeSelect = document.getElementById('mode');
    const singleFileFields = document.getElementById('single-file-fields');
    const twoFileFields = document.getElementById('two-file-fields');
    const singleFileInput = document.getElementById('file');
    const beforeFileInput = document.getElementById('before-file');
    const afterFileInput = document.getElementById('after-file');
    const twoFileModes = new Set(['compare', 'visualize-compare']);
    let latestJob = null;

    modeSelect.addEventListener('change', updateFileInputs);
    updateFileInputs();

    refreshConfig.addEventListener('click', async () => {{
      await loadOperatorData();
    }});

    cleanupJobs.addEventListener('click', async () => {{
      cleanupJobs.disabled = true;
      cleanupResult.textContent = 'Running cleanup...';
      try {{
        const response = await authenticatedFetch('/api/maintenance/cleanup', {{ method: 'POST' }});
        const payload = await response.json();
        cleanupResult.textContent = JSON.stringify(payload, null, 2);
        await loadOperatorData();
      }} catch (error) {{
        cleanupResult.textContent = 'Cleanup failed safely.';
      }} finally {{
        cleanupJobs.disabled = false;
      }}
    }});

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      artifacts.textContent = '';
      metrics.innerHTML = '<p class="empty">Metrics appear after an artifact preview.</p>';
      metadataView.innerHTML = '<p class="empty">Metadata artifact data not loaded.</p>';
      rawJson.textContent = 'No artifact preview loaded.';
      stepProgress.innerHTML = '';
      clearCanvas('waveform');
      clearCanvas('spectrogram');
      visualEmpty.textContent = 'Visualization artifact data not loaded.';
      submit.disabled = true;
      result.textContent = 'Creating job...';
      const token = document.getElementById('token').value;
      const selectedMode = modeSelect.value;
      const isTwoFileMode = twoFileModes.has(selectedMode);
      const data = new FormData();
      data.append('mode', selectedMode);
      if (isTwoFileMode) {{
        data.append('before_file', beforeFileInput.files[0]);
        data.append('after_file', afterFileInput.files[0]);
      }} else {{
        data.append('file', singleFileInput.files[0]);
      }}
      try {{
        const response = await fetch(isTwoFileMode ? '/api/compare-jobs' : '/api/jobs', {{
          method: 'POST',
          headers: {{ Authorization: `Bearer ${{token}}` }},
          body: data
        }});
        const payload = await response.json();
        latestJob = payload;
        result.textContent = JSON.stringify(payload, null, 2);
        renderStatus(payload);
        if (response.ok && payload.job_id && Array.isArray(payload.artifacts)) {{
          renderArtifactButtons(payload);
          previewAll.disabled = false;
          await previewArtifacts(payload);
          await loadOperatorData();
        }}
      }} catch (error) {{
        result.textContent = 'Request failed safely.';
      }} finally {{
        submit.disabled = false;
      }}
    }});

    previewAll.addEventListener('click', async () => {{
      if (latestJob) await previewArtifacts(latestJob);
    }});

    function updateFileInputs() {{
      const isTwoFileMode = twoFileModes.has(modeSelect.value);
      singleFileFields.hidden = isTwoFileMode;
      twoFileFields.hidden = !isTwoFileMode;
      singleFileInput.required = !isTwoFileMode;
      beforeFileInput.required = isTwoFileMode;
      afterFileInput.required = isTwoFileMode;
    }}

    async function loadOperatorData() {{
      try {{
        const configResponse = await authenticatedFetch('/api/config');
        if (configResponse.ok) {{
          renderConfig(await configResponse.json());
        }}
        const jobsResponse = await authenticatedFetch('/api/jobs');
        if (jobsResponse.ok) {{
          renderRecentJobs(await jobsResponse.json());
        }}
      }} catch (error) {{
        configView.innerHTML = '<p class="empty">Operator data request failed safely.</p>';
      }}
    }}

    async function authenticatedFetch(url, options = {{}}) {{
      const headers = new Headers(options.headers || {{}});
      headers.set('Authorization', `Bearer ${{document.getElementById('token').value}}`);
      return await fetch(url, {{ ...options, headers }});
    }}

    function renderConfig(config) {{
      const cards = [];
      addCard(cards, 'Local host', config.web_host);
      addCard(cards, 'Local port', config.web_port);
      addCard(cards, 'Max upload', config.max_upload_mib, ' MiB');
      addCard(cards, 'Active jobs', config.max_active_jobs);
      addCard(cards, 'Job TTL', config.job_ttl_hours, ' h');
      addCard(cards, 'Partial TTL', config.partial_ttl_minutes, ' min');
      addCard(cards, 'Single-file modes', (config.single_file_modes || []).join(', '));
      addCard(cards, 'Two-file modes', (config.two_file_modes || []).join(', '));
      addCard(cards, 'Workflows', (config.workflow_modes || []).join(', '));
      addCard(cards, 'Deferred', (config.deferred_modes || []).join(', '));
      configView.innerHTML = cards.length ? cards.join('') : '<p class="empty">No safe config returned.</p>';
    }}

    function renderRecentJobs(payload) {{
      const jobs = Array.isArray(payload.jobs) ? payload.jobs : [];
      if (!jobs.length) {{
        recentJobs.innerHTML = '<p class="empty">No recent jobs found.</p>';
        return;
      }}
      const rows = jobs.map(job => `<tr><td>${{escapeHtml(String(job.job_id || ''))}}</td><td>${{escapeHtml(String(job.workflow_label || job.mode || ''))}}</td><td>${{escapeHtml(String(job.status || ''))}}</td><td>${{escapeHtml(String(job.created_at || ''))}}</td><td>${{escapeHtml((job.artifacts || []).join(', '))}}</td></tr>`);
      recentJobs.innerHTML = `<table><thead><tr><th>Job</th><th>Type</th><th>Status</th><th>Created</th><th>Artifacts</th></tr></thead><tbody>${{rows.join('')}}</tbody></table>`;
    }}

    function renderArtifactButtons(job) {{
      const groups = job.artifact_groups || null;
      if (groups && Object.keys(groups).length) {{
        for (const [group, names] of Object.entries(groups)) {{
          if (!Array.isArray(names) || !names.length) continue;
          const section = document.createElement('div');
          section.className = 'artifact-group';
          const heading = document.createElement('h3');
          heading.textContent = group || 'Artifacts';
          section.appendChild(heading);
          for (const name of names) {{
            addArtifactButtons(section, job.job_id, name);
          }}
          artifacts.appendChild(section);
        }}
        return;
      }}
      for (const name of job.artifacts || []) {{
        addArtifactButtons(artifacts, job.job_id, name);
      }}
    }}

    function addArtifactButtons(container, jobId, name) {{
      const artifactName = normalizeArtifactName(name);
      if (!artifactName) return;
      const label = artifactLabel(artifactName);
      const url = `/api/jobs/${{jobId}}/artifacts/${{encodeURIComponent(artifactName)}}`;
      const preview = document.createElement('button');
      preview.type = 'button';
      preview.textContent = `Preview ${{label}}`;
      preview.addEventListener('click', async () => {{
        const report = await fetchArtifactPreview(artifactName, url);
        if (report) renderArtifact(artifactName, report);
      }});
      const download = document.createElement('button');
      download.type = 'button';
      download.textContent = `Download ${{label}}`;
      download.addEventListener('click', async () => downloadArtifact(url, artifactName));
      container.appendChild(preview);
      container.appendChild(download);
    }}

    async function previewArtifacts(job) {{
      for (const name of job.artifacts || []) {{
        if (name === 'status.json') continue;
        const url = `/api/jobs/${{job.job_id}}/artifacts/${{encodeURIComponent(name)}}`;
        const report = await fetchArtifactPreview(name, url);
        if (report) renderArtifact(name, report);
      }}
    }}

    async function fetchArtifactPreview(name, url) {{
      if (!name.endsWith('.json') && !name.endsWith('.md')) {{
        return {{ message: 'Preview is not available for this artifact type. Download the artifact instead.' }};
      }}
      const response = await authenticatedFetch(url);
      if (!response.ok) {{
        rawJson.textContent = 'Artifact preview failed safely. Download remains available if this artifact is listed for the job.';
        return null;
      }}
      if (name.endsWith('.md')) {{
        return {{ markdown: await response.text() }};
      }}
      return await response.json();
    }}

    async function downloadArtifact(url, name) {{
      const artifactResponse = await authenticatedFetch(url);
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
    }}

    function renderStatus(job) {{
      const values = [
        ['Job ID', job.job_id],
        ['Mode', job.mode],
        ['Workflow', job.workflow_label],
        ['Status', job.status],
        ['Created', job.created_at],
        ['Completed', job.completed_at],
        ['Failed', job.failed_at]
      ].filter(([, value]) => value);
      statusFields.innerHTML = values.map(([label, value]) => `<div class="card"><span>${{label}}</span><strong>${{escapeHtml(String(value))}}</strong></div>`).join('');
      renderSteps(job.steps || []);
    }}

    function renderSteps(steps) {{
      if (!Array.isArray(steps) || !steps.length) {{
        stepProgress.innerHTML = '';
        return;
      }}
      stepProgress.innerHTML = steps.map(step => `<div class="step"><span>${{escapeHtml(String(step.label || step.name || 'Step'))}}</span><strong>${{escapeHtml(String(step.status || 'pending'))}}</strong></div>`).join('');
    }}

    function renderArtifact(name, report) {{
      if (report.message !== undefined) {{
        rawJson.textContent = report.message;
        return;
      }}
      if (report.markdown !== undefined) {{
        rawJson.textContent = report.markdown;
        return;
      }}
      rawJson.textContent = JSON.stringify(report, null, 2);
      renderMetricCards(report);
      if (name === 'visualization.json') renderVisualization(report);
      if (name === 'visual_compare.json') renderVisualization(report);
      if (name === 'metadata.json' || name === 'metadata_before.json' || name === 'metadata_after.json') renderMetadata(report);
    }}

    function renderMetricCards(report) {{
      const source = report.analysis || report;
      const cards = [];
      addCard(cards, 'Peak dBFS', source.peak_dbfs);
      addCard(cards, 'RMS dBFS', source.rms_dbfs);
      addCard(cards, 'Loudness approx', source.loudness_lufs_approx);
      addCard(cards, 'Clipped samples', source.clipping_sample_count);
      addCard(cards, 'Duration', source.duration_seconds, 's');
      addCard(cards, 'Sample rate', source.sample_rate || source.samplerate, 'Hz');
      addCard(cards, 'Channels', source.channel_count || source.channels);
      addCard(cards, 'Release score', report.score);
      const comparison = report.comparison_metrics || {{}};
      addCard(cards, 'RMSE', comparison.rmse);
      addCard(cards, 'MAE', comparison.mean_absolute_error);
      addCard(cards, 'Correlation', comparison.correlation);
      addCard(cards, 'SNR approx', comparison.snr_db_approx, ' dB');
      metrics.innerHTML = cards.length ? cards.join('') : '<p class="empty">No known metric fields found in this artifact.</p>';
    }}

    function addCard(cards, label, value, suffix = '') {{
      if (value === undefined || value === null || value === '') return;
      const formatted = typeof value === 'number' ? Number(value.toFixed ? value.toFixed(3) : value) : value;
      cards.push(`<div class="card"><span>${{label}}</span><strong>${{escapeHtml(String(formatted))}}${{suffix}}</strong></div>`);
    }}

    function renderVisualization(report) {{
      const source = report.candidate || report;
      const peaks = source.waveform_peaks && Array.isArray(source.waveform_peaks.peaks) ? source.waveform_peaks.peaks : [];
      let energy = source.spectrogram && Array.isArray(source.spectrogram.energy_db) ? source.spectrogram.energy_db : [];
      if (!energy.length && report.difference_map && Array.isArray(report.difference_map.energy_delta_db)) {{
        energy = report.difference_map.energy_delta_db;
      }}
      if (peaks.length) drawWaveform(peaks);
      if (energy.length) drawSpectrogram(energy);
      visualEmpty.textContent = peaks.length || energy.length ? '' : 'Visualization artifact data not available.';
    }}

    function drawWaveform(peaks) {{
      const canvas = document.getElementById('waveform');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#58a6ff';
      ctx.lineWidth = Math.max(1, canvas.width / Math.max(peaks.length, 1) * 0.55);
      const mid = canvas.height / 2;
      peaks.forEach((peak, index) => {{
        const x = (index + 0.5) / peaks.length * canvas.width;
        const minY = mid - Number(peak.min || 0) * mid;
        const maxY = mid - Number(peak.max || 0) * mid;
        ctx.beginPath();
        ctx.moveTo(x, minY);
        ctx.lineTo(x, maxY);
        ctx.stroke();
      }});
    }}

    function drawSpectrogram(energy) {{
      const canvas = document.getElementById('spectrogram');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const rows = energy.length;
      const cols = Math.max(...energy.map(row => Array.isArray(row) ? row.length : 0), 0);
      if (!rows || !cols) return;
      for (let y = 0; y < rows; y++) {{
        const row = energy[y] || [];
        for (let x = 0; x < cols; x++) {{
          const db = Number(row[x] ?? -120);
          const norm = Math.max(0, Math.min(1, (db + 120) / 120));
          ctx.fillStyle = `rgb(${{Math.round(30 + norm * 210)}}, ${{Math.round(55 + norm * 130)}}, ${{Math.round(90 + norm * 80)}})`;
          ctx.fillRect(x / cols * canvas.width, y / rows * canvas.height, Math.ceil(canvas.width / cols), Math.ceil(canvas.height / rows));
        }}
      }}
    }}

    function renderMetadata(report) {{
      if (report.metadata && Array.isArray(report.metadata.supported_standard_fields)) {{
        const fields = report.metadata.supported_standard_fields;
        metadataView.innerHTML = `<p class="muted">Supported standard fields: ${{fields.length}}</p><table><tbody>${{fields.map(field => `<tr><td>${{escapeHtml(String(field))}}</td><td>present</td></tr>`).join('')}}</tbody></table>`;
        return;
      }}
      const display = report.metadata_display;
      if (!display || !display.metadata_values) {{
        metadataView.innerHTML = '<p class="empty">No dashboard metadata summary found.</p>';
        return;
      }}
      const rows = Object.entries(display.metadata_values).map(([key, value]) => `<tr><td>${{escapeHtml(key)}}</td><td>${{escapeHtml(String(value.display_value ?? ''))}}</td></tr>`);
      metadataView.innerHTML = `<p class="muted">Detected keys: ${{display.detected_metadata_keys.length}}</p><table><tbody>${{rows.join('')}}</tbody></table>`;
    }}

    function clearCanvas(id) {{
      const canvas = document.getElementById(id);
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }}

    function escapeHtml(value) {{
      return value.replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
    }}

    function normalizeArtifactName(value) {{
      if (typeof value === 'string') return value.trim();
      if (value && typeof value.name === 'string') return value.name.trim();
      if (value && typeof value.artifact_name === 'string') return value.artifact_name.trim();
      return '';
    }}

    function artifactLabel(name) {{
      return name && name.trim() ? name : 'artifact';
    }}
  </script>
</body>
</html>"""


app = create_app()
