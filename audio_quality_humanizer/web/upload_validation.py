"""Upload validation helpers for the optional private web backend."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status


ALLOWED_EXTENSIONS = {
    ".wav",
    ".flac",
    ".mp3",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
    ".aif",
    ".aiff",
}
CHUNK_SIZE = 1024 * 1024


def validate_extension(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.casefold()
    if not suffix:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing audio file extension.")
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audio file extension.")
    return suffix


async def copy_upload_to_disk(upload: UploadFile, destination: Path, max_bytes: int) -> dict[str, object]:
    extension = validate_extension(upload.filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    first_bytes = b""

    with destination.open("wb") as output:
        while True:
            chunk = await upload.read(CHUNK_SIZE)
            if not chunk:
                break
            if not first_bytes:
                first_bytes = chunk[:32]
            total += len(chunk)
            if total > max_bytes:
                output.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="Upload is too large.")
            output.write(chunk)

    if total <= 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    validate_magic_bytes(extension, first_bytes)
    return {
        "extension": extension,
        "size_bytes": total,
        "content_type": upload.content_type,
        "content_type_advisory": True,
    }


def validate_magic_bytes(extension: str, header: bytes) -> None:
    if not _has_expected_magic(extension, header):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio container header was not recognized.")


def _has_expected_magic(extension: str, header: bytes) -> bool:
    if extension == ".wav":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE"
    if extension == ".flac":
        return header.startswith(b"fLaC")
    if extension == ".mp3":
        return header.startswith(b"ID3") or _looks_like_mpeg_frame(header)
    if extension in {".ogg", ".opus"}:
        return header.startswith(b"OggS")
    if extension in {".aif", ".aiff"}:
        return len(header) >= 12 and header[:4] == b"FORM" and header[8:12] in {b"AIFF", b"AIFC"}
    if extension in {".m4a", ".aac"}:
        return b"ftyp" in header[:16]
    return False


def _looks_like_mpeg_frame(header: bytes) -> bool:
    return len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0


def magic_bytes_supported(extension: str) -> bool:
    return extension.casefold() in ALLOWED_EXTENSIONS
