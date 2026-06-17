"""Discovery — Attachment storage service.

Strategi: simpan file di local filesystem di `/app/uploads/discovery/<session_id>/`.
Metadata disimpan di MongoDB (collection `discovery_attachments`).

Validation rules:
- Max 10 MB per file
- Allowed mime/extension: PDF, PNG, JPG/JPEG, XLSX, DOCX
- Max 5 attachments per question (mencegah abuse)
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple
import os
import uuid

UPLOAD_ROOT = Path(os.environ.get("DISCOVERY_UPLOAD_ROOT", "/app/uploads/discovery"))
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_ATTACHMENTS_PER_QUESTION = 5

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".docx"}
ALLOWED_MIME = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Some browsers send these
    "application/octet-stream",  # fallback (validated by extension)
}


class AttachmentValidationError(ValueError):
    pass


def ensure_session_dir(session_id: str) -> Path:
    """Create dir for session if not exists, return path."""
    p = UPLOAD_ROOT / session_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def sanitize_filename(name: str) -> str:
    """Strip path traversal & dangerous chars."""
    base = os.path.basename(name or "").strip()
    if not base:
        base = "untitled"
    # Replace any non-safe chars
    safe = "".join(c if c.isalnum() or c in "._- " else "_" for c in base)
    return safe[:200]  # cap length


def get_extension(filename: str) -> str:
    """Return lowercase extension (with dot) or empty string."""
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1].lower()


def validate_upload(filename: str, mime: str, size: int) -> None:
    """Raise AttachmentValidationError jika invalid."""
    if size <= 0:
        raise AttachmentValidationError("File kosong")
    if size > MAX_FILE_BYTES:
        raise AttachmentValidationError(
            f"File terlalu besar ({size / 1024 / 1024:.1f} MB). Maksimum 10 MB."
        )
    ext = get_extension(filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise AttachmentValidationError(
            f"Ekstensi {ext or '(tanpa ekstensi)'} tidak diizinkan. Yang diterima: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    # mime sometimes not reliable from browser; tolerate kalau ekstensi sudah valid


def save_file_to_disk(session_id: str, raw_bytes: bytes, original_name: str) -> Tuple[str, str]:
    """Simpan file ke disk. Return (stored_filename, full_path_str)."""
    session_dir = ensure_session_dir(session_id)
    ext = get_extension(original_name)
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    full_path = session_dir / stored_filename
    with open(full_path, "wb") as f:
        f.write(raw_bytes)
    return stored_filename, str(full_path)


def delete_file_from_disk(session_id: str, stored_filename: str) -> bool:
    """Delete file. Return True kalau berhasil."""
    p = UPLOAD_ROOT / session_id / stored_filename
    if p.exists() and p.is_file():
        try:
            p.unlink()
            return True
        except OSError:
            return False
    return False


def delete_session_folder(session_id: str) -> None:
    """Delete entire session folder (used on session deletion)."""
    session_dir = UPLOAD_ROOT / session_id
    if not session_dir.exists():
        return
    try:
        for child in session_dir.iterdir():
            if child.is_file():
                child.unlink()
        session_dir.rmdir()
    except OSError:
        pass  # best-effort
