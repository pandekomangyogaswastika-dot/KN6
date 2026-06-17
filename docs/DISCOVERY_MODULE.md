# Discovery E-Questionnaire — Module Documentation

> **Custom web app modul** untuk mengirim discovery questionnaire ke klien (PT. Kain Nusantara).
> Klien akses via link unik tanpa login. Vendor IT pakai data untuk fondasi development ERP.

> **Version 2.1** — tambahan: **Opsi "Lainnya" (isian bebas)** per pertanyaan pilihan + **Kolom Catatan** per pertanyaan
>
> **Version 2.0** — dengan 3 enhancement: **Branching Logic**, **Admin Notification**, **File Upload**

---

## 📋 Highlights

| Aspek | Detail |
|-------|--------|
| **Total Domain** | **14** (Production/Manufacturing dihapus karena KN tidak produksi) |
| **Total Pertanyaan** | **82 critical questions** (5 di antaranya punya branching rule) |
| **Estimasi Pengisian** | ~3.4 jam (dapat dibagi per-PIC) |
| **Answer Types** | radio (single), checkbox (multi), text short/long, number, yes_no, scale_1_5 |
| **Help Tooltip** | ✅ Setiap pertanyaan punya penjelasan non-teknis |
| **Skip Option** | ✅ Setiap pertanyaan boleh dilewati |
| **Opsi "Lainnya"** | ✅ Pertanyaan pilihan (single/multi) punya opsi "Lainnya…" dengan isian bebas (`other_text`) |
| **Kolom Catatan** | ✅ Setiap pertanyaan punya field catatan tambahan (`note`) — opsional, tidak menghitung progress |
| **Branching Logic** | ✅ Per-question show/hide berdasarkan jawaban dependensi |
| **File Attachments** | ✅ Per-question (PDF, PNG, JPG, XLSX, DOCX, max 10MB, 5 file/pertanyaan) |
| **Auto-Save** | ✅ Debounced 700ms, indicator real-time di header |
| **PDF Export** | ✅ Profesional dengan attachment list per question |
| **Access Control** | UUID session ID = token di URL (no login required) |
| **Admin Notification** | ✅ In-app: badge "Baru!" + stats banner + acknowledge button |
| **Testing** | Backend **34/34 tests PASSED (100%)** (iteration_3.json) |

---

## 🗂 14 Domain (PIC by Role)

| # | Domain | Recommended PIC | Q | Min |
|---|--------|-----------------|---|-----|
| 1 | Profil Perusahaan & Tujuan Strategis | CEO / Owner | 7 | 15 |
| 2 | Kondisi Sistem Existing & Pain Points | CEO + IT + Operations | 7 | 20 |
| 3 | Proses Pembelian (P2P) | Procurement Manager | 6 | 15 |
| 4 | **Gudang & Manajemen Stok** ⚡ | Warehouse Manager | **10** | **30** |
| 5 | Penjualan & Distribusi | Sales Manager | 8 | 20 |
| 6 | Finance & Akunting | CFO / Chief Accountant | 7 | 20 |
| 7 | RFID & Identifikasi Otomatis | Operations + IT | 6 | 15 |
| 8 | Integrasi Sistem | IT Manager | 5 | 12 |
| 9 | Master Data & Migrasi | IT + Domain Owners | 5 | 12 |
| 10 | Infrastruktur & Network | IT / Network Admin | 4 | 10 |
| 11 | Keamanan & Compliance | IT / Compliance | 4 | 10 |
| 12 | Change Management & Training | HR + CEO | 4 | 10 |
| 13 | Vendor, Budget & Timeline | CEO + CFO | 5 | 10 |
| 14 | Tambahan & Catatan Akhir | Semua PIC | 4 | 5 |

> ⚡ Domain 4 (Gudang & Stok) paling kritikal — paling banyak pertanyaan & waktu paling lama.

---

## 🚀 Cara Pakai

### Untuk Vendor (Anda):

1. **Buka admin console:** `https://questionnaire-intake-1.preview.emergentagent.com/discovery`
2. Klik **"Buat Session Baru"** → isi nama klien + project + contact
3. Link otomatis ter-copy ke clipboard (format: `/discovery/<uuid>`)
4. **Kirim link** ke klien via email/WA
5. Klien isi sendiri (boleh sebagian, boleh skip, auto-save)
6. Setelah klien submit (atau kapan saja), klik **"PDF"** di admin → dapat dokumen profesional 17 halaman

### Untuk Klien:

1. Buka link yang dikirim vendor
2. Lihat dashboard 14 domain dengan progress ring per domain
3. Klik domain → mulai isi
4. Setiap pertanyaan ada ikon **(?)** untuk penjelasan non-teknis
5. Boleh **Lewati** kalau tidak tahu/tidak relevan
6. Pindah domain bebas — progress tersimpan otomatis
7. Klik **Ringkasan** untuk review semua jawaban
8. **Submit Final** kalau yakin (mengunci jawaban)
9. Bisa **Export PDF** kapan saja

---

## 🛠 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                       │
│  ┌──────────────────────┐    ┌──────────────────────────┐   │
│  │   Main ERP App       │    │   Discovery App          │   │
│  │   (with login)       │    │   (NO LOGIN, standalone) │   │
│  │   sidebar + routes   │    │   /discovery/*            │   │
│  └──────────────────────┘    └──────────────────────────┘   │
│  └───── index.js routes berdasarkan window.location ─────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                       │
│  /api/discovery/                                            │
│  ├─ GET    /questions             (static dataset)          │
│  ├─ POST   /sessions              (create + UUID token)     │
│  ├─ GET    /sessions/{id}         (load state)              │
│  ├─ PATCH  /sessions/{id}/answers (batch upsert)            │
│  ├─ POST   /sessions/{id}/submit  (lock)                    │
│  ├─ GET    /sessions/{id}/export.pdf  (ReportLab PDF)       │
│  ├─ GET    /sessions              (admin: list all)         │
│  └─ DELETE /sessions/{id}         (admin: delete + cascade) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       MongoDB                               │
│  ├─ discovery_sessions  (id, client_name, status, ...)      │
│  └─ discovery_answers   (session_id, question_id, value)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Map

### Backend
- `/app/backend/routers/discovery.py` — 9 endpoints
- `/app/backend/services/discovery_questions.py` — 14 domain × 82 pertanyaan (static dataset)
- `/app/backend/services/discovery_pdf.py` — ReportLab-based PDF generator (17 halaman profesional)
- `/app/backend/server.py` — router registration

### Frontend
- `/app/frontend/src/index.js` — route bootstrap (detect `/discovery/*`)
- `/app/frontend/src/features/discovery/`
  - `DiscoveryApp.jsx` — entry point, path parser
  - `DiscoveryClient.jsx` — main client experience (load + autosave + nav)
  - `DiscoveryAdmin.jsx` — vendor console (create + list + share link)
  - `DiscoveryInvalid.jsx` — fallback untuk URL invalid
  - `discovery.css` — design tokens (calm professional brand)
  - `api.js` — axios wrapper
  - `components/`
    - `DiscoveryHeader.jsx` — sticky header dengan progress + autosave indicator
    - `DiscoveryDashboard.jsx` — 14 domain cards grid
    - `DomainQuestionnaire.jsx` — single-domain form with prev/next
    - `DiscoverySummary.jsx` — review all + submit final + export PDF
    - `QuestionField.jsx` — polymorphic input (7 types)
    - `HelpButton.jsx` — popover dengan penjelasan non-teknis
    - `ProgressRing.jsx` — SVG circular progress

---

## 🎨 Design Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--discovery-primary` | `#0F4C81` (deep blue) | Brand, primary buttons, headers |
| `--discovery-accent` | `#1D7874` (teal) | Secondary actions, success indicators |
| `--discovery-warn` | `#C77700` (amber) | Skip state, warnings |
| `--discovery-danger` | `#B00020` (deep red) | Destructive, error |
| `--discovery-success` | `#2E7D32` (green) | Answered, completed |
| `--discovery-soft` | `#EEF3F8` | Selected state background |
| `--discovery-bg` | `#F4F6F8` | Page background |

Font: **Figtree** (modern, friendly, profesional)

---

## ✅ Testing Results

```
GET /api/discovery/questions                ✓ Returns 14 domains, 82 questions
POST /api/discovery/sessions                ✓ Creates session with UUID + share_url
GET /api/discovery/sessions/{id}             ✓ Returns metadata + answers + progress
GET .../invalid-uuid                         ✓ Returns 400
GET .../valid-but-not-exist                  ✓ Returns 404
PATCH .../answers (7 types)                  ✓ Batch save all answer types
PATCH dengan invalid question_id             ✓ Silently skipped
POST .../submit                              ✓ Locks status to "submitted"
PATCH setelah submit                         ✓ Returns 403
GET .../export.pdf                           ✓ Valid PDF (37KB, 17 halaman)
GET /sessions (list)                         ✓ Sorted desc by created_at
DELETE /sessions/{id}                        ✓ Cascade deletes answers
Progress calculation                         ✓ Excludes skipped, per-domain accurate
Session state mgmt                           ✓ Draft → Submitted transition
All 7 answer types                           ✓ Handled correctly

Total: 15/15 PASSED (100%)
```

---

## 🔮 Future Enhancements (Optional)

- [x] ~~Branching/conditional logic per question~~ ✅ **DONE (v2.0)**
- [x] ~~File upload per question~~ ✅ **DONE (v2.0)**
- [x] ~~In-app admin notification (badge + stats)~~ ✅ **DONE (v2.0)**
- [ ] Email/WhatsApp notification (external service integration)
- [ ] Multi-language support (EN version for international clients)
- [ ] Multi-PIC support per session (klien team collaborate)
- [ ] Versioning (snapshot pre-submit untuk audit)
- [ ] Analytics dashboard (response rate per domain across clients)

---

## 🆕 Version 2.1 — Opsi "Lainnya" & Kolom Catatan

**Tujuan:** klien tidak terkunci pada opsi yang disediakan + bisa memberi konteks tambahan.

**Data model (`discovery_answers`):** 2 field baru
- `other_text` (string, opsional) — isian bebas saat opsi "Lainnya" dipilih
- `note` (string, opsional) — catatan tambahan per pertanyaan

**Backend:**
- `AnswerPayload` menerima `other_text` + `note`; disimpan via PATCH `/answers`
- Konstanta `OTHER_SENTINEL = "__other__"` + helper `is_answer_filled()` di `discovery_questions.py`
- Progress **value-aware**: jawaban dengan note saja (tanpa value) TIDAK dihitung terisi; opsi "Lainnya" dihitung terisi hanya jika `other_text` diisi
- PDF: render `Lainnya: <other_text>` + baris `Catatan: <note>` per pertanyaan

**Frontend:**
- `single_choice` & `multi_choice` menampilkan opsi "Lainnya…" (border dashed) → reveal input bebas
- "Lainnya" pada multi_choice TIDAK memakai kuota `max_select`
- Setiap pertanyaan punya tombol "Tambah catatan" → textarea catatan (auto-tampil bila sudah terisi)
- Merge-patch autosave (`patchAnswer`) supaya value / other_text / note tersimpan independen tanpa saling menimpa
- Summary menampilkan "Lainnya: …" dan blok "Catatan: …"

---

## 🆕 Version 2.0 — Enhancements Detail

### 1. Branching Logic (Per-Question Show/Hide)

**Backend:**
- Helper `evaluate_show_if(rule, answers_map)` di `services/discovery_questions.py`
- Operator: `equals`, `not_equals`, `in`, `not_in`, `includes`, `not_includes`, `is_truthy`, `is_falsy`
- **Default-show**: kalau dependensi belum dijawab → pertanyaan tetap visible
- `_compute_progress()` filter hidden questions → progress.total = visible count
- PDF generator skip hidden questions

**Frontend:**
- `branching.js` — `shouldShowQuestion()`, `filterVisibleQuestions()`
- DomainQuestionnaire dynamically filter pertanyaan
- Banner info "X pertanyaan otomatis disembunyikan"
- Summary view skip hidden questions

**Contoh rules:**
| Question | Show If |
|----------|---------|
| D06-Q03 (Pajak relevan) | D06-Q02 (PKP status) != "non_pkp" |
| D06-Q05 (Auto bank reconciliation) | D06-Q04 (Jumlah rekening) != "1" |
| D07-Q04 (Tipe RFID) | D07-Q02 (Tujuan RFID) not includes "exploratory" |
| D07-Q05 (Jumlah RFID gate) | D07-Q02 (Tujuan RFID) not includes "exploratory" |
| D08-Q04 (Integrasi e-Faktur) | D06-Q02 (PKP status) != "non_pkp" |

---

### 2. Admin Notification (In-App)

**Backend:**
- Field `acknowledged_at` di session document
- `POST /api/discovery/sessions/{id}/acknowledge` — mark as seen
- `GET /api/discovery/stats` — aggregate (total/submitted/draft/new_submissions/latest_submission)
- Submit reset `acknowledged_at` → null (vendor harus acknowledge ulang)
- List sessions enriched dengan `is_new_submission` flag

**Frontend:**
- Stats banner 4 cards (Submission Baru / Total / Submitted / Submisi Terakhir)
- Badge "Baru!" animated pulse di session card yang submitted & belum di-acknowledge
- Auto-refresh setiap 30 detik
- Tombol "Tandai Sudah Dibaca" per session

---

### 3. File Upload (Local Filesystem)

**Backend:**
- Service: `services/discovery_attachments.py` — validation, sanitize, save/delete
- Storage: `/app/uploads/discovery/<session_id>/<uuid>.<ext>`
- Validasi: max 10 MB, allowed: PDF, PNG, JPG, JPEG, XLSX, DOCX
- Limit: max 5 attachment per question
- Endpoints:
  - `POST /sessions/{id}/attachments` (multipart: question_id + file)
  - `GET /sessions/{id}/attachments` (list)
  - `GET /sessions/{id}/attachments/{att_id}/download`
  - `DELETE /sessions/{id}/attachments/{att_id}`
- Submit lock: 403 saat coba upload/delete setelah session submitted
- Cascade delete: `DELETE /sessions/{id}` hapus folder + semua file di disk

**Frontend:**
- Komponen `AttachmentUploader.jsx` di setiap question card
- Drag-and-drop file picker (native input file)
- Show: filename + size + icon (PDF/PNG/JPG/XLSX/DOCX)
- Download & Delete button per attachment
- Counter "Lampiran (X/5)"
- Client-side validation (size & extension) sebelum upload
- Tampil sebagai badge di Summary view

**PDF Output:**
- Per-question block include section "📎 Lampiran (N): filename.pdf, ..."

---

## ✅ Testing Results

```
=== Iteration 2 (initial module) ===
Total: 15/15 PASSED (100%)

=== Iteration 3 (v2.0 enhancements) ===
BRANCHING (4 tests)
  ✓ Questions return 82 with 5 having show_if
  ✓ Save D06-Q02=non_pkp → progress.total drops to 80
  ✓ Change to pkp → progress.total back to 82
  ✓ PDF export excludes hidden questions

NOTIFICATION (5 tests)
  ✓ Submit resets acknowledged_at to null
  ✓ GET /stats returns all 5 fields
  ✓ List has is_new_submission=true after submit
  ✓ POST /acknowledge sets timestamp
  ✓ Submit again after acknowledge returns 400

FILE UPLOAD (11 tests)
  ✓ Upload PDF/PNG succeeds (201)
  ✓ Reject .zip (400)
  ✓ Reject >10MB (400)
  ✓ Reject invalid question_id (400)
  ✓ Enforce max 5 per question
  ✓ List sorted desc
  ✓ Session GET includes attachments grouped
  ✓ Download returns file content
  ✓ Delete removes metadata + disk file
  ✓ Submit lock for upload/delete (403)
  ✓ Cascade delete on session removal

Total v2.0: 34/34 PASSED (100%)
```

---

**Status:** ✅ **LIVE** & **PRODUCTION-READY** (untuk vendor internal use).
**Tested:** Backend 100%. Frontend manual tested via screenshots — semua flow berfungsi.
**Akses:**
- Admin: https://questionnaire-intake-1.preview.emergentagent.com/discovery
- Klien: https://questionnaire-intake-1.preview.emergentagent.com/discovery/{session-id}
