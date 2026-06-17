"""Discovery PDF generator — professional report layout via ReportLab.

Output format:
- Cover page (client name, project, session id, timestamp)
- Executive summary table (progress per domain)
- Per-domain pages (question + answer + status)
- Footer with page number & generation timestamp
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from services.discovery_questions import evaluate_show_if, OTHER_SENTINEL


# ─── Brand colors (calm professional palette) ────────────────────────────────
PRIMARY = colors.HexColor("#0F4C81")   # deep blue
ACCENT = colors.HexColor("#1D7874")    # teal
MUTED = colors.HexColor("#6C757D")     # gray
LIGHT = colors.HexColor("#F4F6F8")     # near-white
SUCCESS = colors.HexColor("#2E7D32")
WARN = colors.HexColor("#C77700")
DANGER = colors.HexColor("#B00020")
BORDER = colors.HexColor("#D9DEE5")


# ─── Style sheet ─────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=22, leading=28,
            textColor=PRIMARY, spaceAfter=6, alignment=TA_LEFT,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=12, leading=16,
            textColor=MUTED, spaceAfter=18,
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=15, leading=20,
            textColor=PRIMARY, spaceBefore=10, spaceAfter=8,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=12, leading=16,
            textColor=PRIMARY, spaceBefore=8, spaceAfter=4,
        ),
        "DomainHeader": ParagraphStyle(
            "DomainHeader", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=16, leading=22,
            textColor=colors.white, backColor=PRIMARY,
            borderPadding=8, leftIndent=4, spaceBefore=6, spaceAfter=10,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=colors.HexColor("#222"), alignment=TA_JUSTIFY, spaceAfter=4,
        ),
        "Question": ParagraphStyle(
            "Question", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=10.5, leading=14,
            textColor=colors.HexColor("#1A1A1A"), spaceAfter=2,
        ),
        "Help": ParagraphStyle(
            "Help", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=8.5, leading=11,
            textColor=MUTED, leftIndent=8, spaceAfter=2,
        ),
        "AnswerText": ParagraphStyle(
            "AnswerText", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, leading=13,
            textColor=colors.HexColor("#0E5A39"), leftIndent=8, spaceAfter=10,
        ),
        "AnswerSkipped": ParagraphStyle(
            "AnswerSkipped", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=10, leading=13,
            textColor=WARN, leftIndent=8, spaceAfter=10,
        ),
        "AnswerEmpty": ParagraphStyle(
            "AnswerEmpty", parent=base["Normal"],
            fontName="Helvetica-Oblique", fontSize=10, leading=13,
            textColor=DANGER, leftIndent=8, spaceAfter=10,
        ),
        "Small": ParagraphStyle(
            "Small", parent=base["Normal"],
            fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED,
        ),
        "PICRow": ParagraphStyle(
            "PICRow", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, leading=12,
            textColor=ACCENT, spaceAfter=8,
        ),
    }
    return styles


# ─── Page header & footer ────────────────────────────────────────────────────

def _on_page(canvas, doc, *, client_name: str, generated_at: str):
    canvas.saveState()
    # Top border line
    canvas.setStrokeColor(PRIMARY)
    canvas.setLineWidth(2)
    canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    # Header text
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(PRIMARY)
    canvas.drawString(2 * cm, A4[1] - 1.1 * cm, "ERP DISCOVERY REPORT")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.1 * cm, client_name)

    # Footer
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.0 * cm, f"Generated: {generated_at}")
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, "CONFIDENTIAL — Vendor IT Use Only")
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"Halaman {doc.page}")
    canvas.restoreState()


# ─── Value formatters ────────────────────────────────────────────────────────

def _format_answer_value(question: Dict[str, Any], value: Any, other_text: Optional[str] = None) -> str:
    """Render answer value to human-readable string."""
    qtype = question.get("type")
    other_text = (str(other_text).strip() if other_text else "")
    other_display = f"Lainnya: {other_text}" if other_text else "Lainnya (belum diisi)"
    if value is None or value == "" or value == []:
        return ""

    options_map = {opt["value"]: opt["label"] for opt in question.get("options", [])}

    if qtype == "single_choice":
        if value == OTHER_SENTINEL:
            return other_display
        return options_map.get(str(value), str(value))
    if qtype == "multi_choice":
        if isinstance(value, list):
            parts = []
            for v in value:
                if v == OTHER_SENTINEL:
                    parts.append(other_display)
                else:
                    parts.append(options_map.get(str(v), str(v)))
            return " • " + "\n • ".join(parts)
        return str(value)
    if qtype == "yes_no":
        if isinstance(value, bool):
            return "Ya" if value else "Tidak"
        sval = str(value).lower()
        if sval in ("true", "yes", "ya"):
            return "Ya"
        if sval in ("false", "no", "tidak"):
            return "Tidak"
        return str(value)
    if qtype == "scale_1_5":
        labels = question.get("scale_labels", {})
        label = labels.get(str(value), "")
        return f"{value}/5" + (f"  ({label})" if label else "")
    if qtype in ("text_short", "text_long"):
        return str(value)
    if qtype == "number":
        return str(value)
    return str(value)


def _status_chip(percent: int) -> str:
    if percent >= 100:
        return "✓ Selesai"
    if percent >= 50:
        return f"~ {percent}%"
    if percent > 0:
        return f"… {percent}%"
    return "— Belum"


# ─── Main builder ────────────────────────────────────────────────────────────

def build_pdf(
    *,
    session: Dict[str, Any],
    domains: List[Dict[str, Any]],
    answers_map: Dict[str, Dict[str, Any]],
    progress: Dict[str, Any],
    attachments_by_question: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> bytes:
    """Build PDF and return bytes."""
    attachments_by_question = attachments_by_question or {}
    buffer = BytesIO()
    styles = _build_styles()

    client_name = session.get("client_name", "Klien")
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=1.8 * cm,
        title=f"Discovery Report - {client_name}",
        author="ERP Vendor IT",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height, id="normal",
    )
    template = PageTemplate(
        id="main",
        frames=[frame],
        onPage=lambda c, d: _on_page(c, d, client_name=client_name, generated_at=generated_at),
    )
    doc.addPageTemplates([template])

    story: List[Any] = []

    # ── COVER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("ERP DISCOVERY REPORT", styles["Title"]))
    story.append(Paragraph("Hasil Pengisian Questionnaire 14 Domain", styles["Subtitle"]))
    story.append(Spacer(1, 1 * cm))

    info_rows = [
        ["Klien", session.get("client_name") or "-"],
        ["Project", session.get("project_name") or "-"],
        ["Contact Person", session.get("contact_person") or "-"],
        ["Contact Email", session.get("contact_email") or "-"],
        ["Session ID", session.get("id") or "-"],
        ["Status", (session.get("status") or "draft").upper()],
        ["Created", session.get("created_at") or "-"],
        ["Submitted", session.get("submitted_at") or "—"],
    ]
    info_tbl = Table(info_rows, colWidths=[5 * cm, 11 * cm])
    info_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 1.5 * cm))

    overall = progress.get("percent", 0)
    overall_text = f"<b>Progress Pengisian:</b>  {progress.get('answered', 0)} dari {progress.get('total', 0)} pertanyaan terjawab ({overall}%)"
    story.append(Paragraph(overall_text, styles["Body"]))
    if session.get("notes"):
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"<b>Catatan Internal Vendor:</b> {session['notes']}", styles["Body"]))

    story.append(PageBreak())

    # ── EXECUTIVE SUMMARY (Domain Progress Table) ───────────────────────────
    story.append(Paragraph("Ringkasan Per Domain", styles["H1"]))
    story.append(Paragraph(
        "Ringkasan status pengisian klien per domain. Domain yang belum lengkap perlu di-follow up sebelum proceed ke development.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.4 * cm))

    domain_progress_map = {p["domain_id"]: p for p in progress.get("domains", [])}

    sum_data = [["#", "Domain", "PIC Direkomendasikan", "Jawab", "Status"]]
    for d in domains:
        dp = domain_progress_map.get(d["id"], {})
        sum_data.append([
            str(d.get("number", "")),
            d.get("title", ""),
            ", ".join(d.get("recommended_pic", [])),
            f"{dp.get('answered', 0)}/{dp.get('total', 0)}",
            _status_chip(dp.get("percent", 0)),
        ])

    sum_tbl = Table(sum_data, colWidths=[0.9 * cm, 5.8 * cm, 5.2 * cm, 1.8 * cm, 2.3 * cm], repeatRows=1)
    sum_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (3, 0), (4, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(PageBreak())

    # ── PER DOMAIN DETAIL ───────────────────────────────────────────────────
    for d in domains:
        dp = domain_progress_map.get(d["id"], {})
        story.append(Paragraph(
            f"Domain {d.get('number', '')}.  {d.get('title', '')}",
            styles["DomainHeader"],
        ))
        story.append(Paragraph(
            f"<b>PIC Direkomendasikan:</b> {', '.join(d.get('recommended_pic', []))} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Estimasi Waktu:</b> {d.get('estimated_minutes', '?')} menit &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Jawaban:</b> {dp.get('answered', 0)}/{dp.get('total', 0)}",
            styles["PICRow"],
        ))
        story.append(Paragraph(d.get("description", ""), styles["Body"]))
        story.append(Spacer(1, 0.3 * cm))

        for idx, q in enumerate(d.get("questions", []), start=1):
            if not evaluate_show_if(q.get("show_if"), answers_map):
                # Pertanyaan ter-hide karena branching → tidak relevan, skip dari PDF
                continue
            ans = answers_map.get(q["id"])
            qid_label = f"<font color='#6C757D'>{q['id']}</font>"
            question_text = f"{qid_label} &nbsp; <b>Q{idx}.</b> {q.get('prompt', '')}"

            block: List[Any] = [Paragraph(question_text, styles["Question"])]
            if q.get("help"):
                block.append(Paragraph(f"<i>Help:</i> {q['help']}", styles["Help"]))

            if ans is None:
                block.append(Paragraph("(Belum dijawab)", styles["AnswerEmpty"]))
            elif ans.get("skipped"):
                block.append(Paragraph("(Dilewati oleh klien)", styles["AnswerSkipped"]))
            else:
                formatted = _format_answer_value(q, ans.get("value"), ans.get("other_text"))
                if not formatted.strip():
                    block.append(Paragraph("(Kosong)", styles["AnswerEmpty"]))
                else:
                    # Pre-line for multi_choice (already has bullets)
                    formatted_html = formatted.replace("\n", "<br/>")
                    block.append(Paragraph(f"<b>Jawaban:</b> {formatted_html}", styles["AnswerText"]))

            # Catatan tambahan dari klien (tampil walau value kosong, selama tidak di-skip)
            if ans and not ans.get("skipped"):
                note = (ans.get("note") or "").strip()
                if note:
                    block.append(Paragraph(f"<b>Catatan:</b> {note}", styles["Help"]))

            # Attachments (jika ada)
            q_attachments = attachments_by_question.get(q["id"], [])
            if q_attachments:
                att_lines = []
                for att in q_attachments:
                    size_kb = (att.get("size_bytes", 0) / 1024)
                    size_str = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.0f} KB"
                    att_lines.append(
                        f"&bull; {att.get('original_name', 'file')} "
                        f"<font size='8' color='#6C757D'>({size_str})</font>"
                    )
                block.append(Paragraph(
                    f"<b>📎 Lampiran ({len(q_attachments)}):</b><br/>" + "<br/>".join(att_lines),
                    styles["Help"],
                ))

            story.append(KeepTogether(block))

        story.append(PageBreak())

    # ── CLOSING ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Catatan Akhir", styles["H1"]))
    story.append(Paragraph(
        "Dokumen ini adalah hasil pengisian Discovery Questionnaire oleh klien. "
        "Vendor IT akan menggunakan jawaban-jawaban di atas sebagai dasar finalisasi requirement, "
        "estimasi effort, dan rancangan arsitektur sistem ERP yang akan dibangun.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Pertanyaan yang belum dijawab atau dilewati akan dikonfirmasi via meeting follow-up.",
        styles["Body"],
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
