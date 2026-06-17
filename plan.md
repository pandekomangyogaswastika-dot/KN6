# Development Plan — Kain Nusantara (WMS/ERP) — Smart Guidelines + Seed + Documentation + Discovery E‑Questionnaire (v2.0)

> 📌 **MASTER ROADMAP (dari Assessment Vendor):** lihat `/app/docs/KN_DEVELOPMENT_PLAN_FROM_ASSESSMENT.md` — gap analysis assessment vs sistem eksisting + roadmap 6 fase (Sales, HRD, Purchasing, Finance, Warehouse+RFID, Additional) + BI. Status: DRAFT v1, menunggu konfirmasi prioritas user.

> 🏗️ **INFORMATION ARCHITECTURE (IA) BLUEPRINT:** lihat `/app/docs/KN_14_INFORMATION_ARCHITECTURE.md` — fondasi IA menyeluruh (navigasi + data/entity) untuk seluruh 6 fase + BI, dengan Multi-Entity sebagai lapisan fundamental. Status: **DRAFT v1 — LIVING DOC**.

> ✅ **FASE 0 (Enabler) — SELESAI & TESTED (15 Jun 2026):** Multi-Entity (`business_entities`: ent_ksc/ent_kanda + `entity_id` scoped pada transaksi; master SHARED) · Entity Switcher (TopBar) · Notification Center (`notifications`, generator REAL + dedupe) · field master baru (customer npwp/credit_limit/sales_pic, product harga_pokok/gramasi) · Admin Entities tab. Gates HIJAU (64/0/0, compliance 56/0/0, ux 0 ERROR). testing_agent: backend 39/39, frontend 100%. **NEXT:** Fase 1 (Sales) bila disetujui user.

> 🧩 **FASE 0.5 (Enabler 2) — Multi-Entity Inventory Ownership (Roll-as-SSOT) — ✅ ENABLER IMPLEMENTED (Session #016):** atas arahan user, kepemilikan stok dipisah **per entitas pada level ROLL** (`inventory_rolls` = SSOT fisik), **gudang netral/shared**, `inventory_balances` jadi proyeksi kunci `(product+warehouse+owner_entity)`, **integritas lot** (1 pengiriman idealnya 1 lot; mixed-lot hanya bila qty > lot tunggal + konfirmasi), **inter-company transfer WAJIB** sebelum entitas jual barang entitas lain (extend `warehouse_transfers`), HPP/`unit_cost` ditunda Fase 4. Visibilitas Sales: gudang+owner+lot. **Detail: `docs/KN_15_INVENTORY_OWNERSHIP_LOT.md`** (model 3-lapis, algoritma alokasi owner+lot-aware, 28 edge case, invarian gate baru, migrasi, phasing, sub-decision S1–S8). Keputusan inti D1–D4 **disepakati**; S1–S8 **menunggu konfirmasi** sebelum lock final & coding.

> 🔗 **Lanjutan Session #015 — S1–S16 RESOLVED + process flows:** allocation policy CONFIGURABLE+CLARITY, **taksonomi inventory detail** (bucket fisik+transit+pipeline+derived), **mode sumber/pemenuhan** (from_stock/from_incoming/buy_to_order/special_order/cross_dock/drop_ship/inter_company), **tracking multi-modal** (stok visible TANPA RFID), cross-dock/drop-ship, pegging/earmarking, special-order→MD/Purchasing, pre-order/ATP. **Dokumen baru `docs/KN_16_END_TO_END_PROCESS_FLOWS.md`** (flow Sales/Procurement/WMS-RFID + **Blindspot Register G1–G25** + **Info-Needed Register I1–I15**). KN_15 → v1.3. **NO CODING.** Blocking sebelum Fase 0.5: user jawab Info-Needed I1–I6 (entitas/PKP, produk/atribut, UOM, org/approval, pricing/pajak, pembayaran).
- 🧩 **Sales/Finance + CRM (Session #015 lanjutan):** S22–S35 RESOLVED. Eskalasi alokasi ke Admin · entitas dinamis (no hardcode) · multi-rekening `bank_accounts` + SO pilih rekening tujuan (designation ppn/non_ppn) · Special Order (sord_) detail · **Special Price = `price_approvals` (pra_)** + upload bukti (BUKAN koleksi baru) · master data **SSOT tunggal + metadata smart-search/AI-ready** (Sales/Inventory = VIEW, bukan tabel terpisah) · reserved logic KONFIRMASI sudah ada (balance) → upgrade roll. **CRM-LITE + Sales Force** → dokumen baru **`docs/KN_17_SALES_FORCE_CRM.md`**: customer enhanced (assigned_sales_id wajib, payment_profile kontan/tunai/tempo/dp/bertahap, credit control auto-blokir, segment/tags, contacts), **RBAC row-level (sales kelola customer sendiri)**, customer scoped per-entitas (sama boleh lintas-entitas), **sales_targets/sales_incentives/KPI** (penjualan, dicairkan, collection, target, dll), reminder jatuh tempo, advanced (suggestive selling/product focus/smart search) future-ready. Sinkron ENTITY_REGISTRY (customers + sales_targets/sinc/campaigns/cfu + prefixes). Pertanyaan terbuka Q1–Q5 (basis komisi, ambang kredit, customer_group, dll). **NO CODING.**


## Objectives
- Menjaga baseline ERP demo tetap stabil (backend + frontend) dan mengikuti rule kualitas (no monster files, SSOT, compliance scripts).
- **(COMPLETED)** Menyelesaikan isu Smart Guidelines (Guided Tour) agar:
  1) Highlight target **tajam** (tidak blur).
  2) Menu tour **mengikuti role-based access**.
  3) Tour **tidak stuck di step pertama**: auto-navigate, polling target, dan tooltip selalu terlihat.
- **(COMPLETED)** Menyediakan **seed data realistis** untuk demo end-to-end flow utama (POS/Sales → Orders → WMS).
- **(COMPLETED)** Menyediakan **dokumen assessment komprehensif** (15 domain) + **Executive Summary Deck** untuk kebutuhan konsultasi.
- **(COMPLETED ✅)** Membangun **modul Discovery E‑Questionnaire** sebagai web app terpisah untuk klien PT. Kain Nusantara.
- **(COMPLETED ✅ v2.0)** Upgrade Discovery Module dengan 3 enhancement (sesuai permintaan):
  1) **Branching Logic** (per-question show/hide)
  2) **Admin Notification** (in-app: badge “Baru!” + stats + acknowledge)
  3) **File Upload** (local filesystem per pertanyaan, 10MB max)
  
  **Testing:** backend **34/34** tests PASSED (100%) — `/app/test_reports/iteration_3.json`.
- **(ONGOING, DEFERRED UNTIL APPROVED)** Cleanup technical debt (monster files/duplicate endpoints) — hanya dikerjakan jika diminta, karena fokus utama konsultasi & modul Discovery sudah tercapai dan main ERP development masih “PAUSED” (kecuali modul Discovery yang diminta eksplisit).

---

## Implementation Steps

### Phase 1 — Core Flow POC (Guided Tour Overlay + Role Filter)
**User stories (POC)**
1. Sebagai user, saya ingin elemen yang di-highlight terlihat jelas agar bisa mengikuti instruksi tanpa kebingungan.
2. Sebagai user Sales, saya hanya ingin melihat tour yang relevan dengan Sales.
3. Sebagai user Warehouse, saya hanya ingin melihat tour inbound/outbound/stok.
4. Sebagai Manager, saya ingin melihat tour approval/monitoring.
5. Sebagai Admin, saya ingin melihat semua tour.

**Implementasi**
- GuidedTour UI (Frontend)
  - Update `/app/frontend/src/components/GuidedTour.jsx`:
    - Hapus backdrop overlay fullscreen yang redundan (penyebab target ikut tertutup/dim).
    - Gunakan mekanisme dimming via `box-shadow: 0 0 0 9999px ...` pada highlight wrapper.
    - Tambahkan ring animasi pulse untuk emphasis.
- Tour definitions + role rules
  - Update `/app/frontend/src/data/tourDefinitions.js`:
    - Tambahkan `roles: []` pada setiap tour.
    - Tambahkan helper `getToursForRole(role)`.
- Integrasi menu tour
  - Update `/app/frontend/src/App.js`:
    - Render list tour berdasarkan `getToursForRole(user?.role)`.
    - Tampilkan role badge + jumlah tour.
    - Empty-state bila role tidak punya tour.

**POC Testing (wajib sebelum lanjut)**
- Screenshot test untuk role: Admin, Sales, Warehouse, Manager.
- Verifikasi:
  - Target highlight tidak blur.
  - Menu tour sesuai role.
  - Tooltip tampil.

**Status Phase 1: COMPLETED** ✅

---

### Phase 2 — V1 App Development (Stabilisasi & UX polish minimal)
*(Fokus: memastikan Guided Tour stabil, tidak stuck, dan siap dipakai sebagai onboarding nyata.)*

**User stories (V1 stability)**
1. Sebagai user, saya ingin membuka Help & Tours kapan saja tanpa UI lag.
2. Sebagai user, saya ingin bisa menutup tour dengan aman tanpa mengubah state halaman.
3. Sebagai user, saya ingin tour tidak mengganggu navigasi/tab WMS & Orders.
4. Sebagai user, saya ingin tour auto-navigate mengikuti flow sehingga step tidak mentok.
5. Sebagai user, saya ingin tooltip tidak terpotong (selalu di viewport) meskipun halaman scroll.

**Langkah**
- Guided tour reliability upgrade
  - Update `/app/frontend/src/components/GuidedTour.jsx`:
    - Tambahkan `before` action (auto-click) untuk auto-navigate.
    - Tambahkan polling target (wait until element appears, timeout default 2.5s).
    - Tambahkan dukungan `target` berupa testid **atau CSS selector**.
    - Tambahkan `optional` step yang auto-skip bila target tidak ada.
    - Tambahkan `placement: "center"` untuk step info-only.
    - Perbaiki positioning (fixed coords) + viewport clamping/flip agar tooltip tidak off-screen.
- Data-testid alignment
  - Tambahkan data-testid yang diperlukan tour.
- Perbarui tourDefinitions agar mengikuti flow nyata dan selalu punya target valid.

**Testing akhir fase**
- End-to-end screenshot test untuk flow utama.

**Status Phase 2: COMPLETED** ✅

---

### Phase 3 — Feature Expansion (On-demand)
*(Pembayaran dibatalkan; fase ini difokuskan pada data readiness + dokumentasi + roadmap.)*

**Langkah (dikerjakan)**
- Seed data realism upgrade
- Dokumentasi komprehensif

**Status Phase 3: COMPLETED** ✅

---

### Phase 4 — System Cleanup & Production Readiness
*(Baseline kebersihan sistem untuk persiapan scaling development.)*

**Catatan status terbaru**
- Context scripts sudah ada: `/app/scripts/load_context.sh` dan `/app/scripts/validate_compliance.py`.
- Validator menemukan beberapa file frontend >500 lines dan warning minor.
- Cleanup besar ditunda sampai user meminta (karena prioritas konsultasi & modul discovery sudah selesai).

**Phase 4A — Documentation Foundation** ✅
- PRD / SESSION_LOG / TECH_DECISIONS / KN_08–KN_13 tersedia.

**Phase 4D — Automation Tools** ✅
- `validate_compliance.py` dan `check_nav_map.py` tersedia.

**Phase 4E — Frontend Modularization** ✅ COMPLETED (Session #013 — Tech Debt Paydown)
- Monster files (FAIL) di-refactor menjadi sub-komponen colocated:
  - `features/wms/TransferManagement.jsx` 548 → 266 (sub: `transfer/`)
  - `features/wms/InventoryStockView.jsx` 503 → 216 (sub: `inventory/`)
- Near-limit files di-split:
  - `features/discovery/DiscoveryAdmin.jsx` 485 → 192 (sub: CreateSessionDialog, DiscoveryStatsBanner, DiscoverySessionCard, discoveryFormat)
  - `features/discovery/components/QuestionField.jsx` 438 → 171 (extract `QuestionInput.jsx`)
  - `data/tourDefinitions.js` 341 → 55 (split per-domain `tours/`)
  - `App.css` 527 → 9 (split `styles/` partials)
  - `components/CoreWidgets.jsx` 164 → 121 (extract `LoginScreen.jsx`)
- UX migration backlog (ux_audit) **15 ERROR → 0 ERROR**: loading/empty states ditambah di OrdersView, OrderDashboard, SalesPortal, DocumentsView, AdminView, ProductDetail (+ guardrail heuristic FORM_HINTS refinement).
- Doc/script sync: ENTITY_REGISTRY.md ditambah detail discovery_* ; `validate_compliance.py` known_collections + valid_prefixes di-sync untuk domain discovery.
- **Hasil gates:** validate_compliance **54 PASS / 0 FAIL / 0 WARN**, ux_audit **0 ERROR**, verify_contract OK, data_integrity 64/0/0, endpoint_sweep 0×5xx, api_contract OK.
- **Testing:** regression test (testing agent) — backend 19/19, frontend semua komponen refactor + loading states verified, **0 bug**. `/app/test_reports/iteration_2.json`.

**Status Phase 4: COMPLETED** ✅

---

## FASE 0.5 — ENABLER: Roll-as-SSOT Inventory Ownership (Status: ✅ ENABLER IMPLEMENTED — Session #016)

### Yang diimplementasikan (fondasi/enabler, sesuai KN_15 §13)
- **`inventory_rolls`** (prefix `roll_`) = SSOT fisik. `inventory_balances` jadi PROYEKSI 3-key `(product_id+warehouse_id+owner_entity_id)` dengan bucket DETAIL (available/reserved/committed/picked/packed/quarantine/blocked/damaged → on_hand + transit + derived owned/incoming/atp).
- **`services/roll_service.py`**: `rebuild_balance()`/`rebuild_all_balances()`, `generate_rolls_from_balances()` (migrasi sintetis idempotent — KN_15 §11), `allocate_and_reserve_rolls()` (owner-scoped + FEFO + single-warehouse preference + split roll), `release_order_rolls()`, `set_order_rolls_status()`.
- **Reservasi LEVEL ROLL & OWNER-SCOPED**: SO hanya boleh mereservasi roll milik `entity_id` penjual (D3). create→reserve, approve→commit, cancel/release→available. Konservasi panjang terjaga.
- **Endpoint**: `GET /api/inventory/rolls` (filter owner/lot/status/warehouse), `/api/inventory/balances` owner-aware (+`owner_entity_name`), `POST /api/inventory/initial-stock` membuat roll, `GET /api/products/{id}/stock-breakdown` + `ownership_matrix` (owner×wh×lot) + `rolls[]`.
- **Frontend**: WMS Stok tab kolom **Pemilik** + banner konteks; tab **Rolls** (RollsTable); InitialStockForm + Pemilik/Lot/Grade; Sales ProductDetail **Ownership Matrix**; filter owner mengikuti Entity Switcher global.
- **Gates**: `verify_contract` register `inventory_rolls`; `verify_data_integrity` + L4-ROLL (proyeksi balance==Σrolls, length valid, ref owner/lot, owner-scoped D3) → **72 PASS/0/0**; `validate_compliance` + `inventory_rolls`; FE↔BE contract OK. POC `tests/poc_roll_reservation.py` **18/18 PASS**.
- ENTITY_REGISTRY: `inventory_rolls` + balances buckets di-flip **PROPOSED → IMPLEMENTED**.

### Sub-fase 1.4 (ATP & Fulfillment Modes) — ✅ SELESAI (Session #019, READ-ONLY)
- **`services/fulfillment_service.py`** (BARU): classifier mode pemenuhan per baris SO — waterfall `from_stock → from_incoming(ATP) → inter_company → backorder` (primary_mode by severity); `build_supply_index` (balances + open-PO on_order) ; `status_board` (per produk × entitas × gudang + indikator inter-company). ATP = available + incoming (incoming dari PO terbuka termasuk 'receiving' − received_qty).
- **Endpoint**: `POST /api/sales-orders/preview-allocation` (READ-ONLY, order:view) · `GET /api/inventory/status-board` (product:view). `schemas.py` +`AllocationPreviewIn`. health_check +status-board.
- **Frontend**: CartPanel `FulfillmentInfo` (badge mode + ATP/Stok/Incoming/Inter-Co + backorder + penjelasan) per item via preview-allocation (debounce 350ms); menu **"Status Stok"** (`InventoryStatusBoard.jsx`) tabel per produk + expand entitas/gudang + metrik + search; `utils/fulfillment.js` (SSOT meta), `.fmode-*` pills.
- **Verifikasi**: POC `tests/poc_atp_fulfillment.py` 5/5; testing_agent backend 21/21, frontend 17/18 (1 isu LOW selector, bukan bug). Gate: data_integrity 85/0, health 22/0, api_contract 0 err, sweep 0×5xx, ux 0 ERROR.

### Sub-fase 1.5 (Inter-Company Transfer Flow) — ✅ SELESAI (Session #020, MUTASI)
- **Backend** (ADDITIVE, MUTASI STOK):
  - `routers/transfers.py` diperluas: `POST /api/transfers/inter-company` (buat transfer `transfer_kind: inter_entity`; roll-reserve di sumber; status `pending_approval`); `POST /api/transfers/{id}/approve` (pindah kepemilikan B→E S3: owner_entity_id roll di sumber dipindah ke dest_entity + rebuild_balance keduanya; status `completed`); `POST /api/transfers/{id}/reject` (lepas reservasi roll sumber; status `rejected`); `DELETE /api/transfers/{id}` (cancel + lepas reservasi bila masih waiting).
  - `GET /api/transfers?transfer_kind=inter_entity` filter list hanya inter-entity.
  - Skema baru: `InterCompanyTransferCreate` (source/dest entity, items list, notes).
- **Frontend**:
  - `features/transfers/InterCompanyTransfers.jsx` (BARU, 265 baris): halaman management — list transfer antar-entitas + approve (manager/admin) + reject + badge status (pending/completed/rejected).
  - `features/sales/SalesPortal.jsx`: `handleRequestTransfer` → call `POST /api/transfers/inter-company` dari POS saat mode `inter_company`.
  - `components/CartPanel.jsx`: tombol "Minta Transfer dari {entity}" + badge "Transfer diminta — menunggu approval" setelah request.
  - `config/navigationConfig.js`: route `interco-transfers` "Transfer Antar-Entitas" untuk role warehouse/manager/admin.
  - `App.js`: render `<InterCompanyTransfers>` saat `activeView === "interco-transfers"`.
- **Verifikasi**: testing_agent backend **36/36 (100%)** — create/approve/reject/cancel/list + permission checks; skenario utama KSC→Kanda (ownership movement + stock conservation + preview mode changes). Frontend code review 100%. Gate: data_integrity 85/0, health 22/0, sweep 0×5xx. Laporan: `test_reports/iteration_8.json`.

### Belum (Fase 1 — Sales lanjutan)
- **backorder lifecycle** (status waiting_stock + auto-fulfill saat GR), algoritma alokasi configurable (R1/R2 policy), mixed-lot confirmation UI, pegging/earmarking, HPP/`unit_cost` (Fase 4). Catatan: backorder saat ini INFORMASIONAL di POS; create_order masih owner-scoped (409 bila stok sendiri kurang).

---

## NEW PHASE — Discovery E‑Questionnaire Module (Status: COMPLETED ✅ v2.0)

### Phase Goals
- Membuat **web app terpisah** “Discovery Questionnaire” untuk klien, berbasis sistem yang sama.
- Akses via link: `https://<domain>/discovery/<session_id>` tanpa login.
- **Per-domain breakdown** agar tidak menjadi 1 form panjang.
- Pertanyaan critical, relevan ke development ERP KN, **tanpa domain Production**.
- Setiap pertanyaan:
  - `answer_type` sesuai (radio/checkbox/text/number/scale/yes_no).
  - Ada **help text non-teknis**.
  - `optional` dan dapat di-skip.
- Auto-save jawaban (draft) + resume.
- Sistem membuat:
  - Ringkasan jawaban per domain.
  - Submit Final (lock).
  - Export **PDF profesional**.

### Scope Domain untuk KN (14 Domain)
Mengacu struktur 15 domain assessment, dengan penyesuaian:
- Tetap gunakan domain-domain strategis, process, tech, governance, execution.
- **Hapus Domain Production/Manufacturing**.
- Fokus pertanyaan yang actionable untuk implementasi: sales, purchase, inventory/WMS, finance, RFID, integration, data migration, infra, security, change mgmt, training, timeline.

### Technical Approach

#### Backend (Delivered v1 + Enhancements v2.0)
- Router: `routers/discovery.py` prefix `/api/discovery`
- MongoDB collections:
  - `discovery_sessions` (UUID token, status: draft/submitted/archived, `acknowledged_at`)
  - `discovery_answers` (session_id, question_id, value, skipped, updated_at)
  - `discovery_attachments` (session_id, question_id, file metadata)
- Dataset statis (version-controlled):
  - `/app/backend/services/discovery_questions.py` → 14 domain × 82 pertanyaan
  - Branching helper: `evaluate_show_if()` + `filter_visible_questions()`
- File upload service:
  - `/app/backend/services/discovery_attachments.py` (NEW)
  - Storage: `/app/uploads/discovery/<session_id>/<uuid>.<ext>`
  - Rule: max 10MB/file; allowed: PDF/PNG/JPG/JPEG/XLSX/DOCX; max 5 file/pertanyaan

**Endpoints (Delivered v2.0):**
- Questionnaire
  - `GET  /api/discovery/questions`
- Sessions
  - `POST /api/discovery/sessions`
  - `GET  /api/discovery/sessions/{session_id}` (include `attachments` grouped by question_id)
  - `PATCH /api/discovery/sessions/{session_id}/answers`
  - `POST /api/discovery/sessions/{session_id}/submit` (lock + reset acknowledged_at)
  - `POST /api/discovery/sessions/{session_id}/acknowledge` (admin clear “New”)
  - `GET  /api/discovery/sessions/{session_id}/export.pdf` (PDF includes attachments list; hidden questions excluded)
  - `GET  /api/discovery/sessions` (admin list; include `is_new_submission`)
  - `GET  /api/discovery/stats` (admin banner)
  - `DELETE /api/discovery/sessions/{session_id}` (cascade delete answers + attachments + folder)
- Attachments
  - `GET  /api/discovery/sessions/{session_id}/attachments`
  - `POST /api/discovery/sessions/{session_id}/attachments` (multipart: question_id + file)
  - `GET  /api/discovery/sessions/{session_id}/attachments/{attachment_id}/download`
  - `DELETE /api/discovery/sessions/{session_id}/attachments/{attachment_id}`

- PDF rendering:
  - ReportLab (`reportlab==4.5.1`)
  - Output: profesional (cover + summary table + per-domain detail + closing)
  - **Branching-aware** (hidden question tidak tampil)
  - **Attachment-aware** (lampiran muncul per question)

#### Frontend (Delivered v1 + Enhancements v2.0)
- Standalone app: `/discovery/*` tanpa login.
- Bootstrap routing di `/app/frontend/src/index.js`:
  - Jika pathname mulai `/discovery` → render `DiscoveryApp`
  - Else → render app ERP existing

**UI features (v2.0):**
- Client App
  - Dashboard domain cards + progress ring
  - Domain form: question cards, input sesuai type, skip/clear, help tooltip
  - **Branching:** `branching.js` filter visible question + banner info hidden
  - **Attachments:** `AttachmentUploader` per question (upload, list, download, delete)
  - Auto-save indicator di header
  - Summary view: review semua jawaban (branching-aware) + tampil badge lampiran
  - Submit Final + Export PDF
- Admin Console (Vendor)
  - Create session, copy link, open, PDF, delete
  - **Stats banner:** total sessions, submitted, draft, new submissions, latest submission
  - **New badge:** “Baru!” untuk submission yang belum di-acknowledge
  - Button “Tandai Sudah Dibaca” (acknowledge)
  - Auto-refresh 30 detik

### Security & Governance
- Session ID = token (no login).
- Guardrails:
  - Validasi UUID format (400 invalid format, 404 not found).
  - Session lock setelah submit (403 untuk edit answers dan upload/delete attachment).

### Implementation Steps (Incremental)

**v1 (COMPLETED)**
- Step 0 — Confirm baseline ✅
- Step 1 — Data model + router skeleton (Backend) ✅
- Step 2 — Answer autosave (Backend) ✅
- Step 3 — Discovery Frontend Shell ✅
- Step 4 — Input types + help text ✅
- Step 5 — PDF Export ✅
- Step 6 — Summary + submission ✅
- Step 7 — Testing ✅ (backend 15/15, frontend screenshot smoke test)

**v2.0 Enhancements (COMPLETED)**
- Step 8 — Branching logic
  - Add `show_if` rules to dataset (5 rules)
  - Backend: progress + PDF filter visible questions
  - Frontend: filter visible questions + banner info
- Step 9 — Admin notification
  - Backend: `acknowledged_at`, `GET /stats`, `POST /acknowledge`, `is_new_submission`
  - Frontend: stats banner + “Baru!” badge + acknowledge button
- Step 10 — File upload (local)
  - Backend: new attachment service + endpoints + cascade delete
  - Frontend: AttachmentUploader per question + badges in summary
  - PDF: lampiran listed per question
- Step 11 — Testing v2.0 ✅ backend **34/34** (iteration_3.json)

### Phase Completion Criteria
- ✅ Vendor dapat create session dan mendapatkan link shareable.
- ✅ Klien membuka link tanpa login.
- ✅ Per-domain navigation, tidak jadi satu form panjang.
- ✅ Semua pertanyaan punya help text.
- ✅ Auto-save + resume berjalan.
- ✅ Summary view + Submit Final (lock).
- ✅ Export PDF menghasilkan dokumen profesional.
- ✅ Branching logic bekerja (question show/hide) + progress dihitung dari visible questions.
- ✅ Admin notification bekerja (stats + badge “Baru!” + acknowledge).
- ✅ File upload bekerja (10MB, 5 types, 5/question, cascade delete).
- ✅ Backend tests pass (34/34).

**Dokumentasi modul:** `/app/docs/DISCOVERY_MODULE.md`

---

## Completed Work (as of latest session)
- ✅ Context preservation scripts: `load_context.sh` + `validate_compliance.py`.
- ✅ Comprehensive ERP Assessment (15 domain) dibuat (4 file) di `/app/docs/`.
- ✅ Executive Summary Deck dibuat: `/app/docs/EXECUTIVE_SUMMARY_DECK.md`.
- ✅ Discovery E‑Questionnaire Module built + documented (v1) + tested:
  - Tests: `/app/test_reports/iteration_2.json` (100% backend pass)
- ✅ Discovery Module v2.0 Enhancements shipped + documented + tested:
  - Branching logic (per question)
  - Admin notification (in-app)
  - File upload (local filesystem)
  - Tests: `/app/test_reports/iteration_3.json` (34/34 backend pass)
- ✅ **FASE 1A — Configuration Foundation** (Session prior): `system_settings`/`payment_terms`/`approval_rules` + `config_service` (compute_tax, evaluate_approval, effective settings) + SettingsPanel (Admin → Pengaturan).
- ✅ **FASE 1B — Configuration Consumption** (Session #018): konfigurasi DIKONSUMSI alur nyata:
  - PPN otomatis (DPP/PPN/Grand Total, ikut PKP/non-PKP entitas, mode excluded/included) di Sales Order + Invoice + dokumen.
  - Diskon per-item & per-order (dikontrol toggle settings), term pembayaran dipilih saat buat SO + tampil di dokumen.
  - Approval SO & PO DINAMIS dari `approval_rules` (role_satisfies; auto-approve di bawah threshold; PO inbound task ditunda sampai approve).
  - INVARIAN-SAFE: `item.subtotal=price×qty` & `total_amount=Σsubtotal` tetap GROSS; breakdown di field terpisah.
  - Gate baru INV-DB3 (konsistensi PPN+diskon). Bug fix: ObjectId-embed di order.payments. Seed backfill agar 0 FE↔BE drift.
  - Backlog Critical PRD #2 (diskon) & #3 (PPN 11%) → SELESAI.

---

## Next Actions
**Menunggu arahan user (Vendor IT):**
1. **Fase 1B follow-up (opsional):** split `PurchaseOrderManagement.jsx` (455 baris/90% limit), auto-reservation expiry job (Critical #1), master data validation (#4), order draft auto-save (#5).
2. **Lanjut Fase berikut** (KN_DEVELOPMENT_PLAN_FROM_ASSESSMENT): Fase 2 HRD · Fase 3 Procurement (Supplier Master) · Fase 4 Finance (GL/AP/AR, HPP) · Fase 5 Warehouse+RFID.
3. **Fase 1 Sales lanjutan** (Sub-fase 1.4 ✅ S#019, Sub-fase 1.5 ✅ S#020). Berikutnya: backorder lifecycle (waiting_stock + auto-fulfill saat GR), allocation policy R1/R2 configurable, mixed-lot confirmation UI.

### Arsip Next Actions (Discovery / arsitektur — masih relevan)
- Pilot rollout discovery ke klien nyata; v3 enhancements (multi-PIC, email/WA notif, analytics, versioning).
- Arsitektur core ERP (tanpa coding): Redis stock-lock+cache, WebSocket manager, RFID edge agent (MQTT).

---

## Success Criteria
- Guided Tour (legacy objectives) tetap stabil dan tidak regress.
- Discovery Module v2.0:
  - Link tanpa login bekerja (token URL).
  - Pertanyaan per domain, critical only, Production removed.
  - Help text non-teknis tersedia.
  - Klien dapat skip.
  - Auto-save + resume.
  - Summary view + submit final.
  - Export PDF profesional.
  - **Branching**: show/hide relevansi berjalan, progress dihitung dari visible questions.
  - **Admin notification**: stats banner + badge “Baru!” + acknowledge.
  - **File upload**: 10MB max, allowed types, 5/question, submit lock, cascade delete.
- Quality/Compliance:
  - Tidak menambah monster files baru.
  - `validate_compliance.py` tidak menambah failure baru dari modul Discovery.
  - Backend discovery endpoints stabil (tested 34/34).
