"""Build and installed-wheel validation for release packaging."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        _run([sys.executable, "-m", "build"], cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        output = f"{exc.stdout or ''}{exc.stderr or ''}"
        if "No module named build" in output:
            print('Install dev tools with: python -m pip install -e ".[dev,test]"')
        return 1

    wheel = _latest_wheel(ROOT / "dist")
    if wheel is None:
        print("No wheel found in dist/.")
        return 1

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        venv_dir = temp_dir / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = _venv_python(venv_dir)
        cli = _venv_executable(venv_dir, "ai-humanizer")

        _run([str(python), "-m", "pip", "install", str(wheel)])
        _run([str(cli), "--version"])
        _run([str(cli), "--help"])
        _run([str(cli), "validation-status", "--help"])

        sample_path = temp_dir / "sample.wav"
        analysis_path = temp_dir / "analysis.json"
        doctor_path = temp_dir / "doctor.json"
        _write_sample(python, sample_path)
        _run([str(cli), "analyze", str(sample_path), "--report", str(analysis_path)])
        _run([str(cli), "doctor", str(sample_path), "--report", str(doctor_path)])
        missing = [path for path in (analysis_path, doctor_path) if not path.exists()]
        if missing:
            print("Missing expected installed-wheel report files:")
            for path in missing:
                print(path)
            return 1

    print("Build check passed.")
    return 0


def _latest_wheel(dist_dir: Path) -> Path | None:
    wheels = sorted(dist_dir.glob("audio_quality_humanizer-*.whl"), key=lambda path: path.stat().st_mtime)
    if not wheels:
        return None
    return wheels[-1]


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_executable(venv_dir: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _write_sample(python: Path, sample_path: Path) -> None:
    script = (
        "from pathlib import Path\n"
        "import numpy as np\n"
        "import soundfile as sf\n"
        f"path = Path({str(sample_path)!r})\n"
        "samplerate = 48000\n"
        "t = np.linspace(0.0, 1.0, samplerate, endpoint=False)\n"
        "audio = 0.2 * np.sin(2.0 * np.pi * 440.0 * t)\n"
        "sf.write(path, audio, samplerate)\n"
    )
    _run([str(python), "-c", script])


def _run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {' '.join(command)}")
        if exc.stdout:
            print(exc.stdout)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
