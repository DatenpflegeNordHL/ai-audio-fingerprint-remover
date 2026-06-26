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
        version="0.14.0",
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
  <title>Audio Quality Humanizer</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #090d13; color: #e6edf3; }}
    main {{ width: min(1220px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0; }}
    header {{ display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; border-bottom: 1px solid #243244; padding-bottom: 20px; margin-bottom: 22px; }}
    h1 {{ font-size: 34px; margin: 0 0 8px; font-weight: 760; }}
    h2 {{ font-size: 17px; margin: 0 0 12px; }}
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
    .links button {{ margin: 7px 8px 0 0; width: auto; background: #1f6feb; border-color: #388bfd; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(145px, 1fr)); gap: 10px; }}
    .card {{ border: 1px solid #243244; background: #0b1017; border-radius: 8px; padding: 12px; }}
    .card strong {{ display: block; font-size: 20px; margin-top: 6px; }}
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
      <div class="badge">Private beta / local</div>
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
            <label for="file">Audio file</label>
            <input id="file" name="file" type="file" accept=".wav,.flac,.mp3,.m4a,.aac,.ogg,.opus,.aif,.aiff" required>
            <button id="submit" type="submit">Create job</button>
          </form>
        </section>
        <section class="panel" id="mode-panel">
          <h2>Modes</h2>
          <p class="muted">Supported now</p>
          <ul>{supported}</ul>
          <p class="muted">Deferred</p>
          <ul>{deferred}</ul>
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
          <pre id="result">No job submitted yet.</pre>
        </section>
        <section class="panel" id="artifact-panel">
          <h2>Artifacts</h2>
          <div id="artifacts" class="links"></div>
          <button id="preview-all" type="button" disabled>Preview result</button>
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
    const metrics = document.getElementById('metrics');
    const rawJson = document.getElementById('raw-json');
    const metadataView = document.getElementById('metadata-view');
    const visualEmpty = document.getElementById('visual-empty');
    let latestJob = null;

    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      artifacts.textContent = '';
      metrics.innerHTML = '<p class="empty">Metrics appear after an artifact preview.</p>';
      metadataView.innerHTML = '<p class="empty">Metadata artifact data not loaded.</p>';
      rawJson.textContent = 'No artifact preview loaded.';
      clearCanvas('waveform');
      clearCanvas('spectrogram');
      visualEmpty.textContent = 'Visualization artifact data not loaded.';
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
        latestJob = payload;
        result.textContent = JSON.stringify(payload, null, 2);
        renderStatus(payload);
        if (response.ok && payload.job_id && Array.isArray(payload.artifacts)) {{
          for (const name of payload.artifacts) {{
            const url = `/api/jobs/${{payload.job_id}}/artifacts/${{encodeURIComponent(name)}}`;
            addArtifactButtons(name, url);
          }}
          previewAll.disabled = false;
          await previewArtifacts(payload);
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

    function addArtifactButtons(name, url) {{
      const preview = document.createElement('button');
      preview.type = 'button';
      preview.textContent = `Preview ${{name}}`;
      preview.addEventListener('click', async () => {{
        const report = await fetchJsonArtifact(url);
        if (report) renderArtifact(name, report);
      }});
      const download = document.createElement('button');
      download.type = 'button';
      download.textContent = `Download ${{name}}`;
      download.addEventListener('click', async () => downloadArtifact(url, name));
      artifacts.appendChild(preview);
      artifacts.appendChild(download);
    }}

    async function previewArtifacts(job) {{
      for (const name of job.artifacts || []) {{
        if (name === 'status.json') continue;
        const url = `/api/jobs/${{job.job_id}}/artifacts/${{encodeURIComponent(name)}}`;
        const report = await fetchJsonArtifact(url);
        if (report) renderArtifact(name, report);
      }}
    }}

    async function fetchJsonArtifact(url) {{
      const response = await fetch(url, {{ headers: {{ Authorization: `Bearer ${{document.getElementById('token').value}}` }} }});
      if (!response.ok) {{
        result.textContent = 'Artifact preview failed safely.';
        return null;
      }}
      return await response.json();
    }}

    async function downloadArtifact(url, name) {{
      const artifactResponse = await fetch(url, {{ headers: {{ Authorization: `Bearer ${{document.getElementById('token').value}}` }} }});
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
        ['Status', job.status],
        ['Created', job.created_at],
        ['Completed', job.status === 'completed' ? job.created_at : ''],
        ['Failed', job.status === 'failed' ? job.created_at : '']
      ].filter(([, value]) => value);
      statusFields.innerHTML = values.map(([label, value]) => `<div class="card"><span>${{label}}</span><strong>${{escapeHtml(String(value))}}</strong></div>`).join('');
    }}

    function renderArtifact(name, report) {{
      rawJson.textContent = JSON.stringify(report, null, 2);
      renderMetricCards(report);
      if (name === 'visualization.json') renderVisualization(report);
      if (name === 'metadata.json') renderMetadata(report);
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
      metrics.innerHTML = cards.length ? cards.join('') : '<p class="empty">No known metric fields found in this artifact.</p>';
    }}

    function addCard(cards, label, value, suffix = '') {{
      if (value === undefined || value === null || value === '') return;
      const formatted = typeof value === 'number' ? Number(value.toFixed ? value.toFixed(3) : value) : value;
      cards.push(`<div class="card"><span>${{label}}</span><strong>${{escapeHtml(String(formatted))}}${{suffix}}</strong></div>`);
    }}

    function renderVisualization(report) {{
      const peaks = report.waveform_peaks && Array.isArray(report.waveform_peaks.peaks) ? report.waveform_peaks.peaks : [];
      const energy = report.spectrogram && Array.isArray(report.spectrogram.energy_db) ? report.spectrogram.energy_db : [];
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
  </script>
</body>
</html>"""


app = create_app()
