"""Discovery E-Questionnaire router.

Public access via session_id (UUID) as token in URL.
Vendor creates session via admin UI; klien akses via shareable link.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import io
import uuid

from db import db
from core_utils import now_iso, safe_doc
from services.discovery_questions import (
    get_all_domains,
    get_domain_by_id,
    get_domain_summary,
    get_all_question_ids,
    get_total_questions,
    evaluate_show_if,
    filter_visible_questions,
    is_answer_filled,
)
from services.discovery_pdf import build_pdf
from services.discovery_attachments import (
    AttachmentValidationError,
    validate_upload,
    save_file_to_disk,
    delete_file_from_disk,
    delete_session_folder,
    sanitize_filename,
    get_extension,
    UPLOAD_ROOT,
    MAX_FILE_BYTES,
    MAX_ATTACHMENTS_PER_QUESTION,
    ALLOWED_EXTENSIONS,
)

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=200)
    project_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None


class AnswerPayload(BaseModel):
    question_id: str
    value: Any  # can be str, int, list (multi_choice), bool, etc.
    skipped: bool = False
    other_text: Optional[str] = None  # isian bebas saat opsi "Lainnya" dipilih
    note: Optional[str] = None         # catatan tambahan per pertanyaan


class AnswersBatch(BaseModel):
    answers: List[AnswerPayload]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


async def _get_session_or_404(session_id: str) -> Dict[str, Any]:
    if not _is_valid_uuid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    session = await db.discovery_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def _compute_progress(session_id: str) -> Dict[str, Any]:
    """Hitung progress per domain & overall — sudah memperhitungkan branching (hidden questions)."""
    answers_list = await db.discovery_answers.find(
        {"session_id": session_id},
        {"_id": 0},
    ).to_list(length=500)
    answers_map = {a["question_id"]: a for a in answers_list}
    answered_ids = {a["question_id"] for a in answers_list if is_answer_filled(a)}

    domains_progress = []
    visible_total = 0
    visible_answered = 0
    for d in get_all_domains():
        visible_qs = filter_visible_questions(d, answers_map)
        d_qids = {q["id"] for q in visible_qs}
        d_answered = len(answered_ids & d_qids)
        visible_total += len(d_qids)
        visible_answered += d_answered
        domains_progress.append({
            "domain_id": d["id"],
            "answered": d_answered,
            "total": len(d_qids),
            "percent": round(d_answered / len(d_qids) * 100) if d_qids else 0,
            "status": "completed" if d_qids and d_answered == len(d_qids) else ("in_progress" if d_answered > 0 else "not_started"),
        })

    return {
        "answered": visible_answered,
        "total": visible_total,
        "percent": round(visible_answered / visible_total * 100) if visible_total else 0,
        "domains": domains_progress,
    }


# ─── Public — Get static questions (semua domain + soal) ─────────────────────

@router.get("/questions")
async def list_questions() -> Dict[str, Any]:
    """Public endpoint: return semua domain + pertanyaan untuk frontend.

    Tidak butuh auth karena semua statis (tidak ada data klien).
    """
    return {
        "domains": get_all_domains(),
        "summary": get_domain_summary(),
        "total_questions": get_total_questions(),
    }


# ─── Session: Create (public — vendor pakai untuk generate link klien) ───────

@router.post("/sessions", status_code=201)
async def create_session(payload: SessionCreate) -> Dict[str, Any]:
    """Buat session baru. Returns session_id + shareable URL path."""
    session_id = str(uuid.uuid4())  # UUID4 = token, panjang & unguessable
    session = {
        "id": session_id,
        "client_name": payload.client_name.strip(),
        "project_name": (payload.project_name or "").strip() or None,
        "contact_person": (payload.contact_person or "").strip() or None,
        "contact_email": (payload.contact_email or "").strip() or None,
        "notes": (payload.notes or "").strip() or None,
        "status": "draft",  # draft | submitted | archived
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "submitted_at": None,
        "acknowledged_at": None,  # set by vendor saat finish meninjau submission
    }
    await db.discovery_sessions.insert_one(session)
    return {
        **safe_doc(session),
        "share_url": f"/discovery/{session_id}",
    }


# ─── Session: Get state ──────────────────────────────────────────────────────

@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get session metadata + all current answers + progress + attachments."""
    session = await _get_session_or_404(session_id)
    answers = await db.discovery_answers.find(
        {"session_id": session_id}, {"_id": 0}
    ).to_list(length=500)
    answers_map = {a["question_id"]: a for a in answers}
    progress = await _compute_progress(session_id)

    # Group attachments by question_id (exclude internal stored_filename/full_path)
    attachment_docs = await db.discovery_attachments.find(
        {"session_id": session_id}, {"_id": 0, "stored_filename": 0, "full_path": 0}
    ).sort("uploaded_at", -1).to_list(length=500)
    attachments_by_question: Dict[str, List[Dict[str, Any]]] = {}
    for a in attachment_docs:
        qid = a.get("question_id")
        if qid:
            attachments_by_question.setdefault(qid, []).append(a)

    return {
        "session": safe_doc(session),
        "answers": answers_map,
        "progress": progress,
        "attachments": attachments_by_question,
    }


# ─── Session: Save (batch upsert) ────────────────────────────────────────────

@router.patch("/sessions/{session_id}/answers")
async def save_answers(session_id: str, payload: AnswersBatch) -> Dict[str, Any]:
    """Upsert multiple answers in one call (auto-save)."""
    session = await _get_session_or_404(session_id)
    if session["status"] in ("submitted", "archived"):
        raise HTTPException(status_code=403, detail="Session sudah submitted, tidak bisa diubah")

    valid_qids = set(get_all_question_ids())

    upserts = 0
    for ans in payload.answers:
        if ans.question_id not in valid_qids:
            continue  # skip invalid IDs silently
        other_text = (ans.other_text or "").strip() or None
        note = (ans.note or "").strip() or None
        doc = {
            "session_id": session_id,
            "question_id": ans.question_id,
            "value": ans.value,
            "skipped": bool(ans.skipped),
            "other_text": other_text,
            "note": note,
            "updated_at": now_iso(),
        }
        await db.discovery_answers.update_one(
            {"session_id": session_id, "question_id": ans.question_id},
            {"$set": doc},
            upsert=True,
        )
        upserts += 1

    await db.discovery_sessions.update_one(
        {"id": session_id}, {"$set": {"updated_at": now_iso()}}
    )
    progress = await _compute_progress(session_id)
    return {"upserted": upserts, "progress": progress}


# ─── Session: Submit (lock) ──────────────────────────────────────────────────

@router.post("/sessions/{session_id}/submit")
async def submit_session(session_id: str) -> Dict[str, Any]:
    """Mark session as submitted (final, no more edits). Reset acknowledged_at jadi None supaya admin dapat badge 'New'."""
    session = await _get_session_or_404(session_id)
    if session["status"] != "draft":
        raise HTTPException(status_code=400, detail="Session bukan dalam status draft")
    await db.discovery_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": "submitted",
            "submitted_at": now_iso(),
            "updated_at": now_iso(),
            "acknowledged_at": None,  # vendor harus acknowledge ulang setiap submission
        }},
    )
    return {"id": session_id, "status": "submitted"}


@router.post("/sessions/{session_id}/acknowledge")
async def acknowledge_session(session_id: str) -> Dict[str, Any]:
    """Vendor acknowledge sebuah submission (clear 'New' badge di admin)."""
    await _get_session_or_404(session_id)
    await db.discovery_sessions.update_one(
        {"id": session_id},
        {"$set": {"acknowledged_at": now_iso()}},
    )
    return {"id": session_id, "acknowledged_at": now_iso()}


# ─── Session: Export PDF ─────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/export.pdf")
async def export_session_pdf(session_id: str):
    """Generate & return PDF profesional dengan semua jawaban + daftar attachments."""
    session = await _get_session_or_404(session_id)
    answers = await db.discovery_answers.find(
        {"session_id": session_id}, {"_id": 0}
    ).to_list(length=500)
    answers_map = {a["question_id"]: a for a in answers}
    progress = await _compute_progress(session_id)

    attachment_docs = await db.discovery_attachments.find(
        {"session_id": session_id}, {"_id": 0, "stored_filename": 0, "full_path": 0}
    ).to_list(length=500)
    attachments_by_question: Dict[str, List[Dict[str, Any]]] = {}
    for a in attachment_docs:
        qid = a.get("question_id")
        if qid:
            attachments_by_question.setdefault(qid, []).append(a)

    pdf_bytes = build_pdf(
        session=safe_doc(session),
        domains=get_all_domains(),
        answers_map=answers_map,
        progress=progress,
        attachments_by_question=attachments_by_question,
    )

    filename = f"Discovery_Report_{session.get('client_name', 'Client').replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─── Admin: List all sessions ────────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(limit: int = 100) -> List[Dict[str, Any]]:
    """List all sessions (for vendor admin dashboard)."""
    sessions = await db.discovery_sessions.find({}, {"_id": 0}).sort("created_at", -1).to_list(length=limit)
    # Enrich with progress
    enriched = []
    for s in sessions:
        progress = await _compute_progress(s["id"])
        enriched.append({
            **safe_doc(s),
            "progress": progress,
            "is_new_submission": s.get("status") == "submitted" and not s.get("acknowledged_at"),
        })
    return enriched


@router.get("/stats")
async def admin_stats() -> Dict[str, Any]:
    """Aggregate stats untuk Admin dashboard banner."""
    total = await db.discovery_sessions.count_documents({})
    submitted = await db.discovery_sessions.count_documents({"status": "submitted"})
    unack = await db.discovery_sessions.count_documents(
        {"status": "submitted", "acknowledged_at": None}
    )
    # Find latest submission
    latest = await db.discovery_sessions.find(
        {"status": "submitted"}, {"_id": 0, "client_name": 1, "submitted_at": 1, "id": 1}
    ).sort("submitted_at", -1).limit(1).to_list(length=1)
    return {
        "total_sessions": total,
        "submitted_sessions": submitted,
        "draft_sessions": total - submitted,
        "new_submissions": unack,
        "latest_submission": latest[0] if latest else None,
    }


# ─── Admin: Delete a session ─────────────────────────────────────────────────

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """Delete session, all answers, all attachments (metadata + files)."""
    await _get_session_or_404(session_id)
    await db.discovery_answers.delete_many({"session_id": session_id})
    await db.discovery_attachments.delete_many({"session_id": session_id})
    delete_session_folder(session_id)
    await db.discovery_sessions.delete_one({"id": session_id})
    return None


# ─── Attachments ─────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/attachments")
async def list_attachments(session_id: str) -> List[Dict[str, Any]]:
    """List all attachments for a session, grouped by question_id-ready format."""
    await _get_session_or_404(session_id)
    docs = await db.discovery_attachments.find(
        {"session_id": session_id}, {"_id": 0, "stored_filename": 0, "full_path": 0}
    ).sort("uploaded_at", -1).to_list(length=500)
    return docs


@router.post("/sessions/{session_id}/attachments", status_code=201)
async def upload_attachment(
    session_id: str,
    question_id: str = Form(...),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Upload attachment untuk pertanyaan tertentu.

    - Validasi: 10 MB max, allowed types (PDF, PNG, JPG, XLSX, DOCX)
    - Max 5 attachments per question
    - File disimpan di /app/uploads/discovery/{session_id}/<uuid>.<ext>
    """
    session = await _get_session_or_404(session_id)
    if session.get("status") in ("submitted", "archived"):
        raise HTTPException(status_code=403, detail="Session sudah submitted — tidak bisa upload file baru")

    # Validasi question_id
    if question_id not in set(get_all_question_ids()):
        raise HTTPException(status_code=400, detail=f"Invalid question_id: {question_id}")

    # Check kuota per question
    existing_count = await db.discovery_attachments.count_documents({
        "session_id": session_id, "question_id": question_id,
    })
    if existing_count >= MAX_ATTACHMENTS_PER_QUESTION:
        raise HTTPException(
            status_code=400,
            detail=f"Maksimum {MAX_ATTACHMENTS_PER_QUESTION} file per pertanyaan. Hapus file lama dulu.",
        )

    # Baca file & validasi
    raw = await file.read()
    original_name = sanitize_filename(file.filename or "file")
    try:
        validate_upload(original_name, file.content_type or "", len(raw))
    except AttachmentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Simpan ke disk
    stored_filename, full_path = save_file_to_disk(session_id, raw, original_name)

    # Insert metadata
    att_id = str(uuid.uuid4())
    doc = {
        "id": att_id,
        "session_id": session_id,
        "question_id": question_id,
        "original_name": original_name,
        "stored_filename": stored_filename,
        "full_path": full_path,
        "mime_type": file.content_type or "application/octet-stream",
        "extension": get_extension(original_name),
        "size_bytes": len(raw),
        "uploaded_at": now_iso(),
    }
    await db.discovery_attachments.insert_one(doc)
    await db.discovery_sessions.update_one(
        {"id": session_id}, {"$set": {"updated_at": now_iso()}}
    )

    # Return safe doc (exclude internal paths)
    return {
        "id": att_id,
        "session_id": session_id,
        "question_id": question_id,
        "original_name": original_name,
        "mime_type": doc["mime_type"],
        "extension": doc["extension"],
        "size_bytes": doc["size_bytes"],
        "uploaded_at": doc["uploaded_at"],
    }


@router.get("/sessions/{session_id}/attachments/{attachment_id}/download")
async def download_attachment(session_id: str, attachment_id: str):
    """Download single attachment."""
    await _get_session_or_404(session_id)
    doc = await db.discovery_attachments.find_one(
        {"id": attachment_id, "session_id": session_id}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Attachment not found")
    full_path = doc.get("full_path")
    from pathlib import Path
    if not full_path or not Path(full_path).exists():
        raise HTTPException(status_code=410, detail="File hilang di server (rusak/terhapus manual)")
    return FileResponse(
        path=full_path,
        media_type=doc.get("mime_type") or "application/octet-stream",
        filename=doc.get("original_name") or "download",
    )


@router.delete("/sessions/{session_id}/attachments/{attachment_id}", status_code=204)
async def delete_attachment(session_id: str, attachment_id: str):
    """Delete single attachment (file + metadata)."""
    session = await _get_session_or_404(session_id)
    if session.get("status") in ("submitted", "archived"):
        raise HTTPException(status_code=403, detail="Session sudah submitted — tidak bisa hapus file")
    doc = await db.discovery_attachments.find_one(
        {"id": attachment_id, "session_id": session_id}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Attachment not found")
    delete_file_from_disk(session_id, doc.get("stored_filename") or "")
    await db.discovery_attachments.delete_one({"id": attachment_id, "session_id": session_id})
    await db.discovery_sessions.update_one(
        {"id": session_id}, {"$set": {"updated_at": now_iso()}}
    )
    return None
