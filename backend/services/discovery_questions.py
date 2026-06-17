"""Discovery E-Questionnaire — Static question dataset.

Catatan desain:
- 14 domain (Production/Manufacturing DIHAPUS karena PT. Kain Nusantara tidak ada produksi).
- Hanya pertanyaan CRITICAL yang relevan untuk development ERP.
- Setiap pertanyaan: type + help text (non-teknis) + opsi skip.
- Total: ~85 pertanyaan, estimasi pengisian 4-6 jam (split per-PIC).

Answer types:
- 'single_choice'  : radio button (1 opsi)
- 'multi_choice'   : checkbox (banyak opsi)
- 'text_short'     : input text 1 baris
- 'text_long'      : textarea
- 'number'         : input numerik
- 'scale_1_5'      : skala 1-5 (Likert)
- 'yes_no'         : ya/tidak
"""

# Sentinel value untuk opsi "Lainnya" (isian bebas) pada single_choice / multi_choice.
# Saat dipilih, jawaban menyimpan value=OTHER_SENTINEL dan teks bebas di field `other_text`.
OTHER_SENTINEL = "__other__"
OTHER_LABEL = "Lainnya (isi sendiri)"

DISCOVERY_DOMAINS = [
    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 1 — Profil Perusahaan & Tujuan Strategis
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D01",
        "number": 1,
        "code": "company-profile",
        "title": "Profil Perusahaan & Tujuan Strategis",
        "icon": "Building2",
        "color": "blue",
        "recommended_pic": ["CEO / Owner", "Direktur Utama"],
        "estimated_minutes": 15,
        "description": "Memahami profil bisnis, ukuran perusahaan, dan target strategis 3-5 tahun ke depan agar ERP yang dibangun sesuai konteks bisnis Anda.",
        "questions": [
            {
                "id": "D01-Q01",
                "prompt": "Jenis bisnis utama PT. Kain Nusantara?",
                "type": "single_choice",
                "options": [
                    {"value": "distributor", "label": "Distributor / Wholesaler"},
                    {"value": "retailer", "label": "Retailer (B2C)"},
                    {"value": "hybrid", "label": "Hybrid (Wholesale + Retail)"},
                    {"value": "trading", "label": "Trading Company (import/export)"},
                ],
                "help": "Pilih yang paling mendekati. Ini menentukan modul mana yang jadi prioritas (misalnya distributor butuh fitur kontrak harga & rebate, retailer butuh POS).",
            },
            {
                "id": "D01-Q02",
                "prompt": "Berapa total karyawan saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "1-25", "label": "1 – 25 orang"},
                    {"value": "26-50", "label": "26 – 50 orang"},
                    {"value": "51-100", "label": "51 – 100 orang"},
                    {"value": "101-250", "label": "101 – 250 orang"},
                    {"value": "251+", "label": "Lebih dari 250 orang"},
                ],
                "help": "Hitung total karyawan tetap + kontrak. Jumlah ini menentukan jumlah lisensi sistem dan kapasitas server yang diperlukan.",
            },
            {
                "id": "D01-Q03",
                "prompt": "Berapa jumlah lokasi operasional (kantor + gudang + toko)?",
                "type": "single_choice",
                "options": [
                    {"value": "1", "label": "1 lokasi (terpusat)"},
                    {"value": "2-3", "label": "2 – 3 lokasi"},
                    {"value": "4-10", "label": "4 – 10 lokasi"},
                    {"value": "10+", "label": "Lebih dari 10 lokasi"},
                ],
                "help": "Jumlah lokasi fisik yang aktif beroperasi. Ini mempengaruhi desain multi-warehouse dan sinkronisasi data antar cabang.",
            },
            {
                "id": "D01-Q04",
                "prompt": "Apakah PT. Kain Nusantara bagian dari group perusahaan / punya anak perusahaan?",
                "type": "yes_no",
                "help": "Group structure mempengaruhi apakah ERP harus mendukung multi-entity (laporan konsolidasi, transfer antar entity, dll).",
            },
            {
                "id": "D01-Q05",
                "prompt": "Target pertumbuhan revenue dalam 3 tahun ke depan?",
                "type": "single_choice",
                "options": [
                    {"value": "stable", "label": "Stabil (pertumbuhan < 10%/tahun)"},
                    {"value": "moderate", "label": "Moderat (10 – 30%/tahun)"},
                    {"value": "aggressive", "label": "Agresif (30 – 100%/tahun)"},
                    {"value": "explosive", "label": "Sangat agresif (> 100%/tahun, ekspansi besar)"},
                ],
                "help": "Target pertumbuhan menentukan arsitektur skalabilitas sistem. Pertumbuhan agresif butuh infrastruktur yang siap scale 3-5x tanpa rebuild.",
            },
            {
                "id": "D01-Q06",
                "prompt": "Apa 3 tujuan utama dari investasi ERP & RFID ini? (pilih maksimal 3)",
                "type": "multi_choice",
                "max_select": 3,
                "options": [
                    {"value": "stock_accuracy", "label": "Akurasi stok > 99%"},
                    {"value": "scalability", "label": "Skalabilitas tanpa nambah headcount banyak"},
                    {"value": "real_time", "label": "Real-time visibility & faster decision"},
                    {"value": "cost_reduction", "label": "Cost reduction (efisiensi operasional)"},
                    {"value": "compliance", "label": "Compliance & audit readiness (untuk IPO/audit eksternal)"},
                    {"value": "customer_service", "label": "Customer service level meningkat"},
                    {"value": "integration", "label": "Integrasi e-commerce / omnichannel"},
                    {"value": "automation", "label": "Otomatisasi proses manual"},
                ],
                "help": "Fokus pada tujuan paling kritis. Ini akan jadi success criteria di akhir proyek — sistem dianggap berhasil kalau tujuan ini tercapai.",
            },
            {
                "id": "D01-Q07",
                "prompt": "Catatan tambahan tentang visi atau business case (opsional)",
                "type": "text_long",
                "help": "Apapun yang ingin Anda sampaikan tentang arah bisnis: ekspansi pasar baru, rencana IPO, akuisisi, dll. Kosongkan jika tidak relevan.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 2 — Kondisi Sistem Existing & Pain Points
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D02",
        "number": 2,
        "code": "current-state",
        "title": "Kondisi Sistem Existing & Pain Points",
        "icon": "AlertTriangle",
        "color": "amber",
        "recommended_pic": ["CEO / Owner", "IT Manager", "Operations Head"],
        "estimated_minutes": 20,
        "description": "Memahami sistem yang sedang dipakai dan masalah-masalah utama yang ingin diselesaikan dengan ERP baru.",
        "questions": [
            {
                "id": "D02-Q01",
                "prompt": "Bagaimana sistem pencatatan transaksi saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "manual_paper", "label": "Manual / Buku tulis / Form kertas"},
                    {"value": "excel_only", "label": "Excel / Google Sheet"},
                    {"value": "accounting_software", "label": "Software accounting (Accurate / Zahir / Jurnal)"},
                    {"value": "custom_app", "label": "Aplikasi custom in-house"},
                    {"value": "erp_lama", "label": "Sudah pakai ERP tapi mau ganti"},
                    {"value": "mixed", "label": "Campuran beberapa sistem di atas"},
                ],
                "help": "Penting untuk strategi migrasi data. Kalau dari Excel, butuh proses cleansing lebih intensif. Kalau dari ERP lama, ada API extract yang lebih cepat.",
            },
            {
                "id": "D02-Q02",
                "prompt": "Software / tools apa saja yang sedang digunakan saat ini? (pilih semua yang relevan)",
                "type": "multi_choice",
                "options": [
                    {"value": "accurate", "label": "Accurate"},
                    {"value": "zahir", "label": "Zahir"},
                    {"value": "jurnal", "label": "Jurnal (Mekari)"},
                    {"value": "moka_pos", "label": "Moka POS"},
                    {"value": "excel", "label": "Microsoft Excel / Google Sheets"},
                    {"value": "tokopedia", "label": "Marketplace: Tokopedia"},
                    {"value": "shopee", "label": "Marketplace: Shopee"},
                    {"value": "tiktok_shop", "label": "Marketplace: TikTok Shop"},
                    {"value": "lazada", "label": "Marketplace: Lazada"},
                    {"value": "whatsapp_business", "label": "WhatsApp Business untuk order"},
                    {"value": "custom", "label": "Aplikasi custom buatan internal"},
                    {"value": "none", "label": "Tidak ada / Manual saja"},
                ],
                "help": "Daftar lengkap tools yang aktif. Ini menentukan strategi integrasi (apa yang harus tetap, apa yang akan diganti).",
            },
            {
                "id": "D02-Q03",
                "prompt": "Seberapa parah pain point 'selisih stok' di gudang saat ini?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Tidak ada masalah", "3": "Sedang", "5": "Sangat parah, sering rugi"},
                "help": "Selisih stok = perbedaan antara catatan sistem vs fisik di gudang. Skala 5 berarti hampir setiap bulan ada item hilang/lebih yang tidak bisa dijelaskan.",
            },
            {
                "id": "D02-Q04",
                "prompt": "Seberapa parah pain point 'laporan terlambat / tidak akurat'?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Laporan real-time", "3": "Mingguan", "5": "Bulanan / sering salah"},
                "help": "Sebagai management, seberapa sering Anda mendapat laporan operasional yang up-to-date dan akurat untuk pengambilan keputusan?",
            },
            {
                "id": "D02-Q05",
                "prompt": "Seberapa parah pain point 'human error pada data entry'?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Hampir tidak ada", "3": "Cukup sering", "5": "Setiap hari"},
                "help": "Misal: salah input qty, salah pilih customer, salah harga. Dampaknya: invoice salah, complaint customer, rugi finansial.",
            },
            {
                "id": "D02-Q06",
                "prompt": "Estimasi kerugian finansial per bulan akibat masalah sistem saat ini (Rp)?",
                "type": "single_choice",
                "options": [
                    {"value": "under_10jt", "label": "Di bawah Rp 10 juta"},
                    {"value": "10_50jt", "label": "Rp 10 – 50 juta"},
                    {"value": "50_100jt", "label": "Rp 50 – 100 juta"},
                    {"value": "100_500jt", "label": "Rp 100 – 500 juta"},
                    {"value": "500jt_plus", "label": "Di atas Rp 500 juta"},
                    {"value": "unknown", "label": "Belum pernah dihitung"},
                ],
                "help": "Estimasi total kerugian: selisih stok, dead stock, labor inefisiensi, customer complaint, dll. Tidak perlu presisi, cukup range.",
            },
            {
                "id": "D02-Q07",
                "prompt": "Tiga pain points teratas yang PALING ingin diselesaikan (urutkan prioritas)",
                "type": "text_long",
                "help": "Tulis 3 hal yang paling mengganggu operasional saat ini. Contoh: 1) Stok opname 5 hari, 2) Laporan baru bisa H+7, 3) Customer sering complain pesanan salah.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 3 — Proses Pembelian (Purchase / P2P)
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D03",
        "number": 3,
        "code": "procurement",
        "title": "Proses Pembelian (Purchase to Pay)",
        "icon": "ShoppingCart",
        "color": "purple",
        "recommended_pic": ["Procurement Manager", "Finance Manager"],
        "estimated_minutes": 15,
        "description": "Memahami alur pembelian dari permintaan barang sampai pembayaran ke supplier.",
        "questions": [
            {
                "id": "D03-Q01",
                "prompt": "Berapa rata-rata jumlah Purchase Order (PO) per bulan?",
                "type": "single_choice",
                "options": [
                    {"value": "under_10", "label": "Di bawah 10 PO/bulan"},
                    {"value": "10_50", "label": "10 – 50 PO/bulan"},
                    {"value": "50_200", "label": "50 – 200 PO/bulan"},
                    {"value": "200_500", "label": "200 – 500 PO/bulan"},
                    {"value": "500_plus", "label": "Lebih dari 500 PO/bulan"},
                ],
                "help": "PO = Purchase Order = surat pesanan resmi ke supplier. Volume ini menentukan desain workflow otomatisasi.",
            },
            {
                "id": "D03-Q02",
                "prompt": "Berapa jumlah supplier aktif (yang ada transaksi dalam 12 bulan terakhir)?",
                "type": "single_choice",
                "options": [
                    {"value": "under_20", "label": "Kurang dari 20 supplier"},
                    {"value": "20_50", "label": "20 – 50 supplier"},
                    {"value": "50_200", "label": "50 – 200 supplier"},
                    {"value": "200_plus", "label": "Lebih dari 200 supplier"},
                ],
                "help": "Supplier yang masih aktif kirim barang ke Anda. Jumlah ini menentukan kompleksitas master data supplier.",
            },
            {
                "id": "D03-Q03",
                "prompt": "Bagaimana proses approval PO saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "no_approval", "label": "Tidak ada approval (PR langsung jadi PO)"},
                    {"value": "single_approval", "label": "1 level approval (Manager / Direktur)"},
                    {"value": "tiered", "label": "Berjenjang berdasarkan nominal (mis. < 10jt → Manager, > 10jt → Direktur)"},
                    {"value": "matrix", "label": "Matrix approval (per kategori barang + nominal)"},
                ],
                "help": "Approval = persetujuan sebelum PO dikirim ke supplier. Ini akan jadi rule di sistem (workflow engine).",
            },
            {
                "id": "D03-Q04",
                "prompt": "Term pembayaran ke supplier yang paling umum?",
                "type": "single_choice",
                "options": [
                    {"value": "cod", "label": "COD (bayar saat barang datang)"},
                    {"value": "net_7", "label": "Net 7 hari"},
                    {"value": "net_30", "label": "Net 30 hari"},
                    {"value": "net_60", "label": "Net 60 hari"},
                    {"value": "net_90", "label": "Net 90 hari"},
                    {"value": "mixed", "label": "Bervariasi tergantung supplier"},
                ],
                "help": "Net 30 = pembayaran 30 hari setelah invoice diterima. Ini perlu di-track sistem untuk cash flow forecasting.",
            },
            {
                "id": "D03-Q05",
                "prompt": "Apakah ada supplier yang KRITIKAL (>30% supply tergantung dari 1 supplier)?",
                "type": "yes_no",
                "help": "Supplier kritikal = kalau supplier ini stop kirim, operasional terganggu serius. Penting untuk risk management & supplier scorecard.",
            },
            {
                "id": "D03-Q06",
                "prompt": "Catatan khusus tentang proses pembelian (opsional)",
                "type": "text_long",
                "help": "Misal: ada supplier yang harus pakai sistem khusus, ada produk yang butuh QC inspeksi sebelum diterima, dll.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 4 — Gudang & Manajemen Stok (Paling Critical)
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D04",
        "number": 4,
        "code": "warehouse-inventory",
        "title": "Gudang & Manajemen Stok (Warehouse Management)",
        "icon": "Warehouse",
        "color": "emerald",
        "recommended_pic": ["Warehouse Manager", "Operations Head", "Inventory Controller"],
        "estimated_minutes": 30,
        "description": "Bagian PALING KRITIKAL — ini jantung dari ERP Anda. Akurasi data di sini menentukan keberhasilan sistem.",
        "questions": [
            {
                "id": "D04-Q01",
                "prompt": "Berapa jumlah SKU (Stock Keeping Unit / variant produk) yang aktif saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "under_100", "label": "Kurang dari 100 SKU"},
                    {"value": "100_500", "label": "100 – 500 SKU"},
                    {"value": "500_2000", "label": "500 – 2.000 SKU"},
                    {"value": "2000_10000", "label": "2.000 – 10.000 SKU"},
                    {"value": "10000_plus", "label": "Lebih dari 10.000 SKU"},
                ],
                "help": "SKU = setiap variant unik produk (mis. Batik Mega Mendung Biru-XL = 1 SKU, Biru-L = 1 SKU lain). Hitung yang masih aktif dijual.",
            },
            {
                "id": "D04-Q02",
                "prompt": "Bagaimana sistem identifikasi item di gudang saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "no_label", "label": "Tidak ada label, andalkan ingatan staff"},
                    {"value": "manual_label", "label": "Label kertas tulis tangan"},
                    {"value": "barcode_print", "label": "Barcode (dicetak) + scanner"},
                    {"value": "rfid", "label": "Sudah pakai RFID"},
                    {"value": "mixed", "label": "Campuran beberapa metode di atas"},
                ],
                "help": "Identifikasi = cara membedakan item satu dengan lain di gudang. Ini critical untuk akurasi picking & opname.",
            },
            {
                "id": "D04-Q03",
                "prompt": "Apakah ada konsep BATCH / LOT / ROLL untuk produk kain?",
                "type": "multi_choice",
                "options": [
                    {"value": "batch", "label": "Batch (kelompok produksi)"},
                    {"value": "lot", "label": "Lot (sub-batch / penomoran fiskal)"},
                    {"value": "roll", "label": "Roll (gulungan kain individual)"},
                    {"value": "color_dyelot", "label": "Color Dyelot (batch pewarnaan)"},
                    {"value": "none", "label": "Tidak ada — produk fungible (interchangeable)"},
                ],
                "help": "Kain umumnya punya variasi warna per gulungan meski SKU sama (dyelot). Ini perlu di-track untuk garansi & matching order besar.",
            },
            {
                "id": "D04-Q04",
                "prompt": "Satuan ukur (Unit of Measure) yang dipakai untuk produk kain?",
                "type": "multi_choice",
                "options": [
                    {"value": "meter", "label": "Meter"},
                    {"value": "yard", "label": "Yard"},
                    {"value": "roll", "label": "Roll / Gulungan"},
                    {"value": "kg", "label": "Kilogram (untuk benang)"},
                    {"value": "pcs", "label": "Pcs (untuk produk jadi)"},
                    {"value": "lembar", "label": "Lembar"},
                ],
                "help": "Sistem harus support konversi otomatis (mis. 1 Roll = 50 Meter). Pilih semua yang Anda pakai sehari-hari.",
            },
            {
                "id": "D04-Q05",
                "prompt": "Bagaimana metode penilaian stok (inventory valuation) saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "fifo", "label": "FIFO (First In First Out)"},
                    {"value": "lifo", "label": "LIFO (Last In First Out)"},
                    {"value": "weighted_avg", "label": "Weighted Average Cost"},
                    {"value": "specific_id", "label": "Specific Identification (per roll/batch)"},
                    {"value": "unknown", "label": "Belum ditetapkan formal"},
                ],
                "help": "Cara menghitung HPP (Harga Pokok Penjualan). Penting untuk akuntansi & pelaporan pajak. Konsultasikan dengan akuntan Anda jika ragu.",
            },
            {
                "id": "D04-Q06",
                "prompt": "Seberapa sering stok opname (cycle count / physical inventory) dilakukan?",
                "type": "single_choice",
                "options": [
                    {"value": "daily", "label": "Setiap hari (cycle count selective)"},
                    {"value": "weekly", "label": "Mingguan"},
                    {"value": "monthly", "label": "Bulanan"},
                    {"value": "quarterly", "label": "Per 3 bulan"},
                    {"value": "yearly", "label": "Tahunan saja"},
                    {"value": "ad_hoc", "label": "Tidak terjadwal / hanya kalau ada masalah"},
                ],
                "help": "Stok opname = pengecekan fisik vs catatan. Frekuensi opname menentukan tingkat akurasi sistem.",
            },
            {
                "id": "D04-Q07",
                "prompt": "Berapa lama waktu yang dibutuhkan untuk 1x stok opname menyeluruh saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "under_1day", "label": "Kurang dari 1 hari"},
                    {"value": "1_3day", "label": "1 – 3 hari"},
                    {"value": "3_7day", "label": "3 – 7 hari (stop operasi)"},
                    {"value": "1_4weeks", "label": "1 – 4 minggu"},
                    {"value": "rarely_done", "label": "Jarang dilakukan menyeluruh"},
                ],
                "help": "Jika opname > 3 hari → biasanya operasional harus stop → opportunity cost besar. RFID bisa mengurangi waktu opname 10x lipat.",
            },
            {
                "id": "D04-Q08",
                "prompt": "Apakah sudah ada konsep ZONE / RACK / BIN di gudang?",
                "type": "single_choice",
                "options": [
                    {"value": "fully_organized", "label": "Sudah lengkap (Zone, Rack, Bin terlabeli)"},
                    {"value": "zone_only", "label": "Hanya Zone (area besar)"},
                    {"value": "informal", "label": "Ada pembagian tapi tidak formal/terlabeli"},
                    {"value": "none", "label": "Belum ada — penempatan ad-hoc"},
                ],
                "help": "Zone = area gudang. Rack = rak. Bin = lokasi spesifik (kotak/slot). Penting untuk picking efisien & lokasi traceable.",
            },
            {
                "id": "D04-Q09",
                "prompt": "Apakah Anda butuh fitur RESERVATION stok (mengunci stok untuk customer tertentu sebelum dikirim)?",
                "type": "yes_no",
                "help": "Misal: customer pesan 100 meter Batik Mega, stok di-LOCK 3 hari sambil tunggu pembayaran. Selama LOCK, customer lain tidak bisa beli stok itu.",
            },
            {
                "id": "D04-Q10",
                "prompt": "Catatan khusus tentang operasional gudang (opsional)",
                "type": "text_long",
                "help": "Misal: kain harus disimpan dengan kelembaban tertentu, ada kategori barang yang butuh handling khusus, dll.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 5 — Penjualan & Distribusi
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D05",
        "number": 5,
        "code": "sales-distribution",
        "title": "Penjualan & Distribusi (Order to Cash)",
        "icon": "TrendingUp",
        "color": "rose",
        "recommended_pic": ["Sales Manager", "Operations Head"],
        "estimated_minutes": 20,
        "description": "Memahami alur penjualan dari quotation, sales order, pengiriman, sampai pembayaran masuk.",
        "questions": [
            {
                "id": "D05-Q01",
                "prompt": "Channel penjualan yang aktif saat ini? (pilih semua)",
                "type": "multi_choice",
                "options": [
                    {"value": "offline_b2b", "label": "Offline B2B (canvasing, kantor, sales lapangan)"},
                    {"value": "offline_b2c", "label": "Offline B2C (toko sendiri)"},
                    {"value": "online_marketplace", "label": "Marketplace (Tokopedia, Shopee, dll)"},
                    {"value": "online_website", "label": "Website e-commerce sendiri"},
                    {"value": "social_commerce", "label": "Social Commerce (IG, WA, FB)"},
                    {"value": "distributor", "label": "Via distributor / mitra reseller"},
                    {"value": "export", "label": "Export (luar negeri)"},
                ],
                "help": "Setiap channel butuh konfigurasi berbeda (harga, term pembayaran, integrasi). Pilih semua yang aktif.",
            },
            {
                "id": "D05-Q02",
                "prompt": "Berapa rata-rata Sales Order (SO) per bulan?",
                "type": "single_choice",
                "options": [
                    {"value": "under_100", "label": "Kurang dari 100 SO/bulan"},
                    {"value": "100_500", "label": "100 – 500 SO/bulan"},
                    {"value": "500_2000", "label": "500 – 2.000 SO/bulan"},
                    {"value": "2000_10000", "label": "2.000 – 10.000 SO/bulan"},
                    {"value": "10000_plus", "label": "Lebih dari 10.000 SO/bulan"},
                ],
                "help": "SO = Sales Order = pesanan yang masuk dari customer. Volume ini menentukan kapasitas sistem & arsitektur queue.",
            },
            {
                "id": "D05-Q03",
                "prompt": "Berapa jumlah customer aktif (transaksi dalam 6 bulan terakhir)?",
                "type": "single_choice",
                "options": [
                    {"value": "under_50", "label": "Kurang dari 50"},
                    {"value": "50_200", "label": "50 – 200"},
                    {"value": "200_1000", "label": "200 – 1.000"},
                    {"value": "1000_5000", "label": "1.000 – 5.000"},
                    {"value": "5000_plus", "label": "Lebih dari 5.000"},
                ],
                "help": "Customer aktif = yang masih transaksi. Penting untuk sizing CRM module.",
            },
            {
                "id": "D05-Q04",
                "prompt": "Apakah ada konsep TIERED PRICING (harga berbeda per segmen customer)?",
                "type": "single_choice",
                "options": [
                    {"value": "uniform", "label": "Tidak — semua customer harga sama"},
                    {"value": "tier_2_3", "label": "Ya — 2-3 tier (mis. Retail / Wholesale)"},
                    {"value": "tier_4plus", "label": "Ya — 4+ tier (mis. Retail / Reseller / Distributor / VIP)"},
                    {"value": "contract", "label": "Ya — per kontrak individual (harga negosiasi)"},
                    {"value": "complex", "label": "Kompleks (kombinasi tier + kontrak + promo)"},
                ],
                "help": "Tiered Pricing = harga berbeda untuk grup customer berbeda. Wholesale biasanya dapat harga lebih murah dari Retail.",
            },
            {
                "id": "D05-Q05",
                "prompt": "Term pembayaran dari customer yang paling umum?",
                "type": "single_choice",
                "options": [
                    {"value": "cash_upfront", "label": "Cash di muka (sebelum kirim)"},
                    {"value": "cod", "label": "COD (bayar saat barang sampai)"},
                    {"value": "net_7", "label": "Net 7 hari"},
                    {"value": "net_30", "label": "Net 30 hari"},
                    {"value": "net_60", "label": "Net 60 hari"},
                    {"value": "mixed", "label": "Campuran berdasarkan customer/kontrak"},
                ],
                "help": "Term pembayaran customer mempengaruhi cash flow & risk management (need credit limit setting).",
            },
            {
                "id": "D05-Q06",
                "prompt": "Bagaimana metode pengiriman barang?",
                "type": "multi_choice",
                "options": [
                    {"value": "own_fleet", "label": "Armada sendiri (truk/mobil milik perusahaan)"},
                    {"value": "rented_fleet", "label": "Armada sewa"},
                    {"value": "expedition_jne", "label": "JNE / J&T / SiCepat / dll (kiriman paket)"},
                    {"value": "expedition_logistic", "label": "Ekspedisi besar (Lion Parcel, Pos Indonesia, dll)"},
                    {"value": "3pl", "label": "3PL / freight forwarder"},
                    {"value": "customer_pickup", "label": "Customer ambil sendiri (pickup di gudang)"},
                ],
                "help": "Method pengiriman mempengaruhi integrasi shipping API & cost calculation di sistem.",
            },
            {
                "id": "D05-Q07",
                "prompt": "Apakah ada Sales Force lapangan yang butuh aplikasi mobile?",
                "type": "yes_no",
                "help": "Sales Force = sales lapangan yang canvasing ke customer. Kalau ya, sistem perlu fitur mobile dengan offline mode & GPS tracking.",
            },
            {
                "id": "D05-Q08",
                "prompt": "Catatan khusus tentang proses penjualan (opsional)",
                "type": "text_long",
                "help": "Misal: ada customer kontraktor yang butuh format invoice khusus, ada produk yang tidak boleh dijual ke wilayah tertentu, dll.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 6 — Finance & Akunting
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D06",
        "number": 6,
        "code": "finance-accounting",
        "title": "Finance & Akunting",
        "icon": "Wallet",
        "color": "indigo",
        "recommended_pic": ["CFO / Finance Manager", "Chief Accountant"],
        "estimated_minutes": 20,
        "description": "Memahami kebutuhan akuntansi, perpajakan, dan pelaporan keuangan.",
        "questions": [
            {
                "id": "D06-Q01",
                "prompt": "Apakah Anda sudah punya Chart of Accounts (COA) formal?",
                "type": "single_choice",
                "options": [
                    {"value": "yes_psak", "label": "Ya — sesuai PSAK / SAK ETAP"},
                    {"value": "yes_custom", "label": "Ya — custom (buatan internal)"},
                    {"value": "partial", "label": "Sebagian saja (belum lengkap)"},
                    {"value": "no", "label": "Belum ada"},
                ],
                "help": "COA = daftar akun (asset, liability, equity, revenue, expense) untuk pembukuan. PSAK = standar akuntansi Indonesia.",
            },
            {
                "id": "D06-Q02",
                "prompt": "Status PKP (Pengusaha Kena Pajak) — apakah PT. Kain Nusantara wajib PPN?",
                "type": "single_choice",
                "options": [
                    {"value": "pkp", "label": "Ya — PKP (wajib pungut PPN 11%)"},
                    {"value": "non_pkp", "label": "Tidak — Non-PKP"},
                    {"value": "planning_pkp", "label": "Sedang proses pengajuan PKP"},
                    {"value": "unknown", "label": "Belum tahu pasti"},
                ],
                "help": "PKP wajib menerbitkan Faktur Pajak (e-Faktur) untuk setiap penjualan. Sistem harus integrasi dengan DJP.",
            },
            {
                "id": "D06-Q03",
                "prompt": "Pajak apa saja yang relevan untuk operasional? (pilih semua)",
                "type": "multi_choice",
                "show_if": {"question_id": "D06-Q02", "operator": "not_equals", "value": "non_pkp"},
                "options": [
                    {"value": "pph21", "label": "PPh 21 (gaji karyawan)"},
                    {"value": "pph23", "label": "PPh 23 (jasa)"},
                    {"value": "pph_final", "label": "PPh Final UMKM"},
                    {"value": "ppn", "label": "PPN 11%"},
                    {"value": "pph_22", "label": "PPh 22 (import)"},
                    {"value": "pph_4_ayat_2", "label": "PPh 4(2) (sewa, jasa konstruksi)"},
                ],
                "help": "Sistem akan menghitung & memotong pajak otomatis. Konsultasikan dengan konsultan pajak Anda kalau ragu.",
            },
            {
                "id": "D06-Q04",
                "prompt": "Berapa banyak rekening bank yang aktif dipakai untuk transaksi bisnis?",
                "type": "single_choice",
                "options": [
                    {"value": "1", "label": "1 rekening"},
                    {"value": "2_3", "label": "2 – 3 rekening"},
                    {"value": "4_10", "label": "4 – 10 rekening"},
                    {"value": "10_plus", "label": "Lebih dari 10 rekening"},
                ],
                "help": "Sistem perlu support multi-bank untuk rekonsiliasi otomatis (matching pembayaran masuk dengan invoice).",
            },
            {
                "id": "D06-Q05",
                "prompt": "Apakah Anda butuh fitur AUTO BANK RECONCILIATION (otomatis cocokin pembayaran masuk dengan invoice)?",
                "type": "single_choice",
                "show_if": {"question_id": "D06-Q04", "operator": "not_in", "values": ["1"]},
                "options": [
                    {"value": "critical", "label": "Sangat butuh — saat ini sangat memakan waktu"},
                    {"value": "nice", "label": "Akan sangat membantu"},
                    {"value": "not_urgent", "label": "Belum urgent — manual masih OK"},
                    {"value": "no_need", "label": "Tidak butuh"},
                ],
                "help": "Auto rekonsiliasi = sistem otomatis cocokkan mutasi bank dengan invoice. Bisa hemat waktu finance 50-80%.",
            },
            {
                "id": "D06-Q06",
                "prompt": "Berapa lama waktu yang dibutuhkan untuk closing bulanan saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "under_5day", "label": "Kurang dari 5 hari kerja"},
                    {"value": "5_10day", "label": "5 – 10 hari kerja"},
                    {"value": "10_20day", "label": "10 – 20 hari kerja"},
                    {"value": "20_plus", "label": "Lebih dari 20 hari kerja"},
                    {"value": "no_closing", "label": "Tidak ada closing rutin"},
                ],
                "help": "Closing = proses tutup buku bulanan (rekonsiliasi, jurnal adjustment, laporan keuangan). Target ERP: closing < 5 hari.",
            },
            {
                "id": "D06-Q07",
                "prompt": "Apakah ada rencana audit eksternal / IPO dalam 2-3 tahun ke depan?",
                "type": "single_choice",
                "options": [
                    {"value": "ipo", "label": "Ada rencana IPO"},
                    {"value": "external_audit", "label": "Audit eksternal rutin"},
                    {"value": "considering", "label": "Sedang dipertimbangkan"},
                    {"value": "no", "label": "Belum ada rencana"},
                ],
                "help": "Audit/IPO butuh audit trail lengkap & laporan formal. Ini mempengaruhi level compliance & security sistem.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 7 — RFID & Identifikasi Otomatis
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D07",
        "number": 7,
        "code": "rfid-assessment",
        "title": "RFID & Identifikasi Otomatis",
        "icon": "Radio",
        "color": "violet",
        "recommended_pic": ["Operations Manager", "IT Manager", "Warehouse Manager"],
        "estimated_minutes": 15,
        "description": "Assessment kebutuhan RFID untuk meningkatkan akurasi stok dan mempercepat operasi gudang.",
        "questions": [
            {
                "id": "D07-Q01",
                "prompt": "Seberapa familiar tim Anda dengan teknologi RFID?",
                "type": "single_choice",
                "options": [
                    {"value": "expert", "label": "Sangat familiar — sudah pernah implementasi"},
                    {"value": "moderate", "label": "Cukup paham konsep dasar"},
                    {"value": "basic", "label": "Sedikit tahu, butuh edukasi"},
                    {"value": "none", "label": "Belum tahu sama sekali"},
                ],
                "help": "RFID = Radio Frequency Identification = tag wireless di setiap item, dibaca otomatis tanpa harus dilihat langsung (beda dengan barcode).",
            },
            {
                "id": "D07-Q02",
                "prompt": "Tujuan utama implementasi RFID? (pilih maks 2)",
                "type": "multi_choice",
                "max_select": 2,
                "options": [
                    {"value": "stock_accuracy", "label": "Akurasi stok > 99%"},
                    {"value": "faster_opname", "label": "Mempercepat stok opname (10x lipat)"},
                    {"value": "reduce_shrinkage", "label": "Mengurangi kehilangan/pencurian"},
                    {"value": "auto_receiving", "label": "Otomatisasi receiving di pintu gudang"},
                    {"value": "auto_shipping", "label": "Otomatisasi verifikasi shipping di pintu keluar"},
                    {"value": "anti_counterfeit", "label": "Anti-pemalsuan produk premium"},
                    {"value": "exploratory", "label": "Masih eksplorasi — belum tahu pasti"},
                ],
                "help": "Pilih tujuan paling utama. RFID adalah investasi besar (~Rp 500jt-1M), pastikan ROI-nya jelas.",
            },
            {
                "id": "D07-Q03",
                "prompt": "Berapa nilai rata-rata per item produk Anda?",
                "type": "single_choice",
                "options": [
                    {"value": "under_50k", "label": "Di bawah Rp 50 ribu/item"},
                    {"value": "50_500k", "label": "Rp 50 ribu – Rp 500 ribu/item"},
                    {"value": "500k_2jt", "label": "Rp 500 ribu – Rp 2 juta/item"},
                    {"value": "2jt_plus", "label": "Di atas Rp 2 juta/item"},
                ],
                "help": "RFID tag harganya ~Rp 500-3000/tag. Untuk produk < Rp 50rb, RFID per-item tidak feasible (tag-per-roll OK).",
            },
            {
                "id": "D07-Q04",
                "prompt": "Tipe RFID yang akan dipakai (jika sudah ada preferensi)?",
                "type": "single_choice",
                "show_if": {"question_id": "D07-Q02", "operator": "not_includes", "values": ["exploratory"]},
                "options": [
                    {"value": "uhf", "label": "UHF (passive, jangkauan 5-10 meter) — paling umum untuk warehouse"},
                    {"value": "hf_nfc", "label": "HF / NFC (jangkauan dekat, untuk anti-counterfeit retail)"},
                    {"value": "active", "label": "Active RFID (battery-powered, untuk aset besar)"},
                    {"value": "tbd", "label": "Belum ditentukan — konsultasikan ke vendor"},
                ],
                "help": "UHF = paling cocok untuk gudang tekstil/distribusi. NFC = cocok untuk retail premium (customer scan dengan HP).",
            },
            {
                "id": "D07-Q05",
                "prompt": "Berapa banyak pintu gudang yang perlu dipasang RFID Gate?",
                "type": "single_choice",
                "show_if": {"question_id": "D07-Q02", "operator": "not_includes", "values": ["exploratory"]},
                "options": [
                    {"value": "0", "label": "0 (handheld scanner saja)"},
                    {"value": "1_2", "label": "1 – 2 pintu"},
                    {"value": "3_5", "label": "3 – 5 pintu"},
                    {"value": "5_plus", "label": "Lebih dari 5 pintu"},
                ],
                "help": "RFID Gate = portal di pintu gudang yang otomatis baca semua tag yang lewat. Per gate ~Rp 80-150jt setup.",
            },
            {
                "id": "D07-Q06",
                "prompt": "Apakah setuju untuk melakukan PROOF OF CONCEPT (POC) RFID dulu sebelum full rollout?",
                "type": "yes_no",
                "help": "POC = uji coba skala kecil (3-4 minggu, 1 SKU, multiple tag type) untuk memastikan RFID benar-benar bekerja di lingkungan Anda. SANGAT DIREKOMENDASIKAN.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 8 — Integrasi Sistem
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D08",
        "number": 8,
        "code": "system-integration",
        "title": "Integrasi Sistem (E-commerce, Banking, dll)",
        "icon": "Network",
        "color": "cyan",
        "recommended_pic": ["IT Manager", "E-commerce Manager"],
        "estimated_minutes": 12,
        "description": "Sistem ERP tidak berdiri sendiri. Identifikasi sistem lain yang perlu terhubung.",
        "questions": [
            {
                "id": "D08-Q01",
                "prompt": "Marketplace / e-commerce yang perlu terintegrasi otomatis? (pilih semua)",
                "type": "multi_choice",
                "options": [
                    {"value": "tokopedia", "label": "Tokopedia"},
                    {"value": "shopee", "label": "Shopee"},
                    {"value": "tiktok_shop", "label": "TikTok Shop"},
                    {"value": "lazada", "label": "Lazada"},
                    {"value": "bukalapak", "label": "Bukalapak"},
                    {"value": "blibli", "label": "Blibli"},
                    {"value": "own_website", "label": "Website e-commerce sendiri"},
                    {"value": "shopify", "label": "Shopify"},
                    {"value": "woocommerce", "label": "WooCommerce / WordPress"},
                    {"value": "none", "label": "Tidak ada / belum perlu"},
                ],
                "help": "Integrasi = order dari marketplace otomatis masuk ERP, stok ter-sync ke semua marketplace real-time.",
            },
            {
                "id": "D08-Q02",
                "prompt": "Software accounting yang harus tetap dipakai (legacy)?",
                "type": "single_choice",
                "options": [
                    {"value": "accurate", "label": "Accurate"},
                    {"value": "zahir", "label": "Zahir"},
                    {"value": "jurnal", "label": "Jurnal (Mekari)"},
                    {"value": "sap", "label": "SAP"},
                    {"value": "oracle", "label": "Oracle"},
                    {"value": "custom", "label": "Custom in-house"},
                    {"value": "none_replace_all", "label": "Tidak ada — ERP baru akan ganti semua"},
                ],
                "help": "Kalau ada legacy accounting yang harus tetap dipakai (mis. karena akuntan eksternal sudah familiar), ERP perlu sync data.",
            },
            {
                "id": "D08-Q03",
                "prompt": "Bank yang dipakai (untuk integrasi mutasi rekening)?",
                "type": "multi_choice",
                "options": [
                    {"value": "bca", "label": "BCA"},
                    {"value": "mandiri", "label": "Mandiri"},
                    {"value": "bni", "label": "BNI"},
                    {"value": "bri", "label": "BRI"},
                    {"value": "cimb", "label": "CIMB Niaga"},
                    {"value": "permata", "label": "Permata"},
                    {"value": "danamon", "label": "Danamon"},
                    {"value": "other", "label": "Bank lain"},
                ],
                "help": "Integrasi bank untuk auto-fetch mutasi rekening → otomatis rekonsiliasi ke invoice. Hemat waktu finance besar.",
            },
            {
                "id": "D08-Q04",
                "prompt": "Apakah perlu integrasi pajak (e-Faktur DJP)?",
                "type": "yes_no",
                "show_if": {"question_id": "D06-Q02", "operator": "not_equals", "value": "non_pkp"},
                "help": "e-Faktur = sistem pajak elektronik dari Direktorat Jenderal Pajak. Wajib untuk PKP. Sistem akan generate faktur pajak otomatis.",
            },
            {
                "id": "D08-Q05",
                "prompt": "Sistem lain yang perlu terhubung (opsional)",
                "type": "text_long",
                "help": "Sebutkan sistem lain seperti HRIS, CRM, BI tools, fleet management, dll. Yang akan diintegrasikan dengan ERP.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 9 — Master Data & Migrasi
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D09",
        "number": 9,
        "code": "data-migration",
        "title": "Master Data & Strategi Migrasi",
        "icon": "Database",
        "color": "teal",
        "recommended_pic": ["IT Manager", "Operations Head", "Finance Manager"],
        "estimated_minutes": 12,
        "description": "60-70% proyek ERP gagal karena data. Memahami kondisi data existing sangat critical untuk strategi migrasi.",
        "questions": [
            {
                "id": "D09-Q01",
                "prompt": "Dimana master data produk saat ini disimpan?",
                "type": "multi_choice",
                "options": [
                    {"value": "excel", "label": "Excel / Google Sheets"},
                    {"value": "accounting_software", "label": "Software accounting"},
                    {"value": "buku_manual", "label": "Buku catatan manual"},
                    {"value": "marketplace", "label": "Tersebar di tiap marketplace"},
                    {"value": "custom_app", "label": "Aplikasi custom in-house"},
                    {"value": "no_master", "label": "Tidak ada master terpusat"},
                ],
                "help": "Master data produk = daftar lengkap SKU, harga, foto, deskripsi, kategori, dll. Sumber data ini akan dimigrasi ke ERP.",
            },
            {
                "id": "D09-Q02",
                "prompt": "Seberapa rapih data produk saat ini?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Berantakan, banyak duplikasi", "3": "Cukup OK", "5": "Sangat rapih, terstandar"},
                "help": "Misal: ada SKU yang ditulis berbeda di tempat berbeda (BTK-001 vs Batik 001), foto tidak konsisten, harga tidak update. Skala 1 = banyak cleansing dibutuhkan.",
            },
            {
                "id": "D09-Q03",
                "prompt": "Seberapa rapih data customer saat ini?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Berantakan, banyak duplikasi", "3": "Cukup OK", "5": "Sangat rapih, terstandar"},
                "help": "Misal: 1 customer ditulis 3 kali dengan nama berbeda, alamat tidak lengkap, NPWP tidak ada. Skala 1 = perlu deduplikasi besar.",
            },
            {
                "id": "D09-Q04",
                "prompt": "Berapa periode historical data yang ingin dimigrasi?",
                "type": "single_choice",
                "options": [
                    {"value": "no_history", "label": "Tidak ada — mulai dari nol di ERP baru"},
                    {"value": "3_months", "label": "3 bulan terakhir"},
                    {"value": "1_year", "label": "1 tahun terakhir"},
                    {"value": "3_years", "label": "3 tahun terakhir"},
                    {"value": "all_history", "label": "Semua riwayat (sebanyak mungkin)"},
                ],
                "help": "Historical data = transaksi lama. Lebih banyak data = lebih lama waktu migrasi. Rekomendasi: 12 bulan untuk reporting & comparison.",
            },
            {
                "id": "D09-Q05",
                "prompt": "Siapa yang akan menjadi DATA STEWARD (penanggung jawab data per domain)?",
                "type": "text_long",
                "help": "Data Steward = 1 orang per area (Sales, Purchase, Inventory, Finance) yang bertanggung jawab data domain itu rapi & akurat sebelum migrasi.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 10 — Infrastruktur & Network
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D10",
        "number": 10,
        "code": "infrastructure",
        "title": "Infrastruktur & Network",
        "icon": "Server",
        "color": "slate",
        "recommended_pic": ["IT Manager", "Network Administrator"],
        "estimated_minutes": 10,
        "description": "Memastikan infrastruktur fisik (server, network, WiFi) siap mendukung ERP.",
        "questions": [
            {
                "id": "D10-Q01",
                "prompt": "Preferensi hosting ERP?",
                "type": "single_choice",
                "options": [
                    {"value": "cloud_saas", "label": "Cloud SaaS (data di server vendor, kami akses via internet)"},
                    {"value": "cloud_private", "label": "Cloud privat (AWS/Azure/GCP — server sewa, data milik kami)"},
                    {"value": "on_premise", "label": "On-Premise (server di kantor kami sendiri)"},
                    {"value": "hybrid", "label": "Hybrid (sebagian cloud, sebagian on-prem)"},
                    {"value": "no_pref", "label": "Belum ada preferensi — rekomendasi dari vendor"},
                ],
                "help": "Cloud = lebih fleksibel & scalable. On-prem = data kontrol penuh tapi maintenance sendiri. Hybrid = kombinasi.",
            },
            {
                "id": "D10-Q02",
                "prompt": "Kondisi internet di kantor pusat / gudang utama?",
                "type": "single_choice",
                "options": [
                    {"value": "fiber_stable", "label": "Fiber stabil (100+ Mbps, jarang putus)"},
                    {"value": "broadband", "label": "Broadband (10-100 Mbps, kadang lambat)"},
                    {"value": "limited", "label": "Terbatas (< 10 Mbps atau sering down)"},
                    {"value": "no_internet", "label": "Tidak ada internet stabil"},
                ],
                "help": "Internet stabil critical untuk cloud ERP. Bandwidth minimum ~10 Mbps per 20 user concurrent.",
            },
            {
                "id": "D10-Q03",
                "prompt": "Apakah ada WiFi coverage di area gudang (untuk handheld scanner)?",
                "type": "single_choice",
                "options": [
                    {"value": "full_coverage", "label": "Coverage penuh, sinyal kuat di seluruh area"},
                    {"value": "partial", "label": "Sebagian area saja"},
                    {"value": "weak", "label": "Ada tapi sinyal lemah"},
                    {"value": "no_wifi", "label": "Tidak ada WiFi di gudang"},
                ],
                "help": "RFID handheld & barcode scanner butuh WiFi stabil di seluruh gudang. Kalau coverage kurang, perlu site survey & install AP tambahan.",
            },
            {
                "id": "D10-Q04",
                "prompt": "Apakah ada strategi backup data formal saat ini?",
                "type": "single_choice",
                "options": [
                    {"value": "automated_offsite", "label": "Otomatis, offsite (cloud backup)"},
                    {"value": "automated_local", "label": "Otomatis tapi local (di server yang sama)"},
                    {"value": "manual", "label": "Manual, sesekali (mis. copy ke external HDD)"},
                    {"value": "no_backup", "label": "Tidak ada backup formal"},
                ],
                "help": "Backup critical untuk Disaster Recovery. Sistem ERP modern harus punya auto-backup harian + offsite copy.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 11 — Keamanan & Compliance
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D11",
        "number": 11,
        "code": "security-compliance",
        "title": "Keamanan & Compliance",
        "icon": "ShieldCheck",
        "color": "red",
        "recommended_pic": ["IT Manager", "Compliance Officer", "CFO"],
        "estimated_minutes": 10,
        "description": "Aspek keamanan data dan kepatuhan terhadap regulasi yang relevan.",
        "questions": [
            {
                "id": "D11-Q01",
                "prompt": "Apakah perusahaan punya kewajiban compliance khusus?",
                "type": "multi_choice",
                "options": [
                    {"value": "iso_27001", "label": "ISO 27001 (Information Security)"},
                    {"value": "iso_9001", "label": "ISO 9001 (Quality Management)"},
                    {"value": "halal", "label": "Sertifikasi Halal"},
                    {"value": "ipo_oojk", "label": "Persiapan IPO (OJK requirements)"},
                    {"value": "uu_pdp", "label": "UU PDP 2022 (Perlindungan Data Pribadi)"},
                    {"value": "tax_audit", "label": "Audit pajak rutin (DJP)"},
                    {"value": "external_audit", "label": "Audit eksternal (KAP)"},
                    {"value": "none_known", "label": "Belum ada / tidak yakin"},
                ],
                "help": "Compliance = kepatuhan terhadap standar/regulasi. Mempengaruhi level security & audit trail di sistem.",
            },
            {
                "id": "D11-Q02",
                "prompt": "Berapa banyak peran (role) yang dibutuhkan di sistem?",
                "type": "single_choice",
                "options": [
                    {"value": "under_5", "label": "Kurang dari 5 role"},
                    {"value": "5_10", "label": "5 – 10 role"},
                    {"value": "10_20", "label": "10 – 20 role"},
                    {"value": "20_plus", "label": "Lebih dari 20 role"},
                ],
                "help": "Role = posisi/jabatan dengan permission berbeda (mis. Sales, Manager, Admin, Warehouse, Cashier). Lebih banyak role = lebih kompleks RBAC.",
            },
            {
                "id": "D11-Q03",
                "prompt": "Apakah butuh fitur Two-Factor Authentication (2FA)?",
                "type": "single_choice",
                "options": [
                    {"value": "all_users", "label": "Ya, semua user wajib"},
                    {"value": "critical_only", "label": "Hanya untuk role critical (Admin, Finance)"},
                    {"value": "optional", "label": "Optional (user bisa aktifkan sendiri)"},
                    {"value": "no", "label": "Belum perlu"},
                ],
                "help": "2FA = login butuh password + kode OTP dari HP. Sangat dianjurkan untuk role critical (Admin, Finance, CEO).",
            },
            {
                "id": "D11-Q04",
                "prompt": "Apakah ada kebutuhan audit trail khusus (siapa, kapan, ubah apa)?",
                "type": "yes_no",
                "help": "Audit trail = log semua perubahan data. Wajib untuk audit eksternal & IPO. Sistem mencatat: siapa login, kapan, ubah field apa, dari nilai apa ke apa.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 12 — Change Management & Training
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D12",
        "number": 12,
        "code": "change-management",
        "title": "Manajemen Perubahan & Pelatihan",
        "icon": "Users",
        "color": "amber",
        "recommended_pic": ["HR Manager", "CEO", "Operations Head"],
        "estimated_minutes": 10,
        "description": "Sistem terbaik pun gagal kalau user tidak adopt. Memahami tingkat kesiapan organisasi.",
        "questions": [
            {
                "id": "D12-Q01",
                "prompt": "Bagaimana tingkat literasi teknologi rata-rata karyawan?",
                "type": "scale_1_5",
                "scale_labels": {"1": "Sangat rendah (banyak yang anti tech)", "3": "Sedang (terbiasa Excel/HP)", "5": "Sangat tinggi (digital native)"},
                "help": "Literasi tech = kemampuan pakai komputer/HP untuk kerja. Mempengaruhi durasi & metode training.",
            },
            {
                "id": "D12-Q02",
                "prompt": "Apakah pernah ada proyek IT besar sebelumnya?",
                "type": "single_choice",
                "options": [
                    {"value": "successful", "label": "Pernah & sukses"},
                    {"value": "partial", "label": "Pernah & hasilnya sebagian sukses"},
                    {"value": "failed", "label": "Pernah & gagal / mengecewakan"},
                    {"value": "never", "label": "Belum pernah"},
                ],
                "help": "Pengalaman sebelumnya menentukan tingkat resistensi tim & lessons learned yang bisa dipakai.",
            },
            {
                "id": "D12-Q03",
                "prompt": "Apakah Anda siap menugaskan SUPER USER (3-10 orang internal yang dilatih intensif)?",
                "type": "single_choice",
                "options": [
                    {"value": "yes_committed", "label": "Ya, sudah ada kandidat & siap commit"},
                    {"value": "yes_will_assign", "label": "Ya, akan menugaskan saat proyek dimulai"},
                    {"value": "maybe", "label": "Pertimbangan, tergantung beban kerja"},
                    {"value": "no", "label": "Tidak — semua user dilatih sama saja"},
                ],
                "help": "Super User = expert internal yang jadi bridge antara user umum & vendor. KRITIKAL untuk sustainability sistem pasca go-live.",
            },
            {
                "id": "D12-Q04",
                "prompt": "Preferensi metode training?",
                "type": "multi_choice",
                "options": [
                    {"value": "classroom", "label": "Classroom (tatap muka, di kantor)"},
                    {"value": "online_live", "label": "Online live (Zoom/Teams)"},
                    {"value": "video_self_paced", "label": "Video tutorial self-paced"},
                    {"value": "documentation", "label": "Dokumentasi tertulis (manual book)"},
                    {"value": "on_the_job", "label": "On the job training (sambil kerja)"},
                ],
                "help": "Pilih semua metode yang cocok. Biasanya kombinasi: classroom + video + on-the-job paling efektif.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 13 — Vendor, Budget & Timeline
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D13",
        "number": 13,
        "code": "vendor-budget",
        "title": "Vendor, Budget & Timeline",
        "icon": "Banknote",
        "color": "green",
        "recommended_pic": ["CEO / Owner", "CFO"],
        "estimated_minutes": 10,
        "description": "Konteks komersial: budget, timeline, dan ekspektasi terhadap vendor.",
        "questions": [
            {
                "id": "D13-Q01",
                "prompt": "Range budget yang Anda siapkan untuk implementasi ERP + RFID (5 tahun total)?",
                "type": "single_choice",
                "options": [
                    {"value": "under_500jt", "label": "Di bawah Rp 500 juta"},
                    {"value": "500jt_2m", "label": "Rp 500 juta – Rp 2 Miliar"},
                    {"value": "2m_5m", "label": "Rp 2 – 5 Miliar"},
                    {"value": "5m_10m", "label": "Rp 5 – 10 Miliar"},
                    {"value": "10m_plus", "label": "Lebih dari Rp 10 Miliar"},
                    {"value": "no_budget_yet", "label": "Belum ditetapkan — tunggu proposal vendor"},
                ],
                "help": "Range budget membantu vendor menyesuaikan scope. Tidak perlu presisi, cukup ballpark.",
            },
            {
                "id": "D13-Q02",
                "prompt": "Timeline ekspektasi untuk go-live?",
                "type": "single_choice",
                "options": [
                    {"value": "3_months", "label": "3 bulan (sangat agresif)"},
                    {"value": "6_months", "label": "6 bulan (agresif)"},
                    {"value": "9_12_months", "label": "9 – 12 bulan (standard)"},
                    {"value": "12_18_months", "label": "12 – 18 bulan (conservative)"},
                    {"value": "flexible", "label": "Fleksibel — yang penting hasil baik"},
                ],
                "help": "Timeline standard untuk ERP+RFID adalah 9-12 bulan. Lebih cepat = risk lebih tinggi.",
            },
            {
                "id": "D13-Q03",
                "prompt": "Strategi implementasi yang dipreferensikan?",
                "type": "single_choice",
                "options": [
                    {"value": "phased", "label": "Phased (bertahap modul per modul)"},
                    {"value": "big_bang", "label": "Big Bang (semua live bersamaan)"},
                    {"value": "pilot_first", "label": "Pilot dulu di 1 lokasi, lalu rollout"},
                    {"value": "no_pref", "label": "Belum ada preferensi — rekomendasi vendor"},
                ],
                "help": "Phased = aman tapi lebih lama. Big Bang = cepat tapi risk tinggi. Pilot = paling sehat untuk multi-lokasi.",
            },
            {
                "id": "D13-Q04",
                "prompt": "Siapa Executive Sponsor untuk proyek ini?",
                "type": "single_choice",
                "options": [
                    {"value": "ceo_owner", "label": "CEO / Owner langsung"},
                    {"value": "director", "label": "Direktur (bukan CEO)"},
                    {"value": "manager", "label": "Manager level"},
                    {"value": "not_yet", "label": "Belum ada / belum ditunjuk"},
                ],
                "help": "Executive Sponsor = decision maker tertinggi yang visible mendukung proyek. KRITIKAL — tanpa sponsor visible, proyek pasti gagal change management.",
            },
            {
                "id": "D13-Q05",
                "prompt": "Tingkat support yang Anda harapkan dari vendor?",
                "type": "single_choice",
                "options": [
                    {"value": "247", "label": "24/7 (sangat critical)"},
                    {"value": "business_hours", "label": "Jam kerja (8x5)"},
                    {"value": "best_effort", "label": "Best effort (response < 24 jam)"},
                    {"value": "self_service", "label": "Self-service (documentation + ticketing)"},
                ],
                "help": "SLA Support mempengaruhi harga maintenance. 24/7 paling mahal. Standard di Indonesia: 8x5 + emergency escalation.",
            },
        ],
    },

    # ────────────────────────────────────────────────────────────────────
    # DOMAIN 14 — Tambahan & Catatan Akhir
    # ────────────────────────────────────────────────────────────────────
    {
        "id": "D14",
        "number": 14,
        "code": "additional-notes",
        "title": "Tambahan & Catatan Akhir",
        "icon": "MessageSquare",
        "color": "neutral",
        "recommended_pic": ["Semua PIC / Free-form"],
        "estimated_minutes": 5,
        "description": "Hal-hal lain yang ingin Anda sampaikan namun belum ter-cover di domain sebelumnya.",
        "questions": [
            {
                "id": "D14-Q01",
                "prompt": "Apakah ada fitur SPESIFIK yang Anda harapkan ada di sistem (yang belum disebut di atas)?",
                "type": "text_long",
                "help": "Misal: mobile app untuk owner monitoring, dashboard TV display untuk warehouse, integrasi dengan WhatsApp untuk notifikasi customer, dll.",
            },
            {
                "id": "D14-Q02",
                "prompt": "Apakah ada KEKHAWATIRAN / RISIKO yang Anda lihat untuk proyek ini?",
                "type": "text_long",
                "help": "Misal: takut downtime saat go-live, takut tim tidak adopsi, takut data hilang saat migrasi, dll. Jujur akan membantu vendor mitigate.",
            },
            {
                "id": "D14-Q03",
                "prompt": "Apa kriteria sukses #1 yang membuat Anda akan bilang 'Proyek ini SUKSES BESAR'?",
                "type": "text_long",
                "help": "1 kalimat yang menggambarkan outcome ideal di akhir proyek. Ini akan jadi pegangan utama tim vendor.",
            },
            {
                "id": "D14-Q04",
                "prompt": "Pertanyaan / hal lain yang ingin Anda tanyakan ke vendor IT?",
                "type": "text_long",
                "help": "Apapun yang ingin Anda klarifikasi. Vendor akan respond di meeting follow-up.",
            },
        ],
    },
]


def get_all_domains():
    """Return list of all domains (with questions inline)."""
    return DISCOVERY_DOMAINS


def get_domain_by_id(domain_id: str):
    """Return single domain by ID, or None."""
    for d in DISCOVERY_DOMAINS:
        if d["id"] == domain_id:
            return d
    return None


def get_question_by_id(question_id: str):
    """Return single question by ID, with parent domain info."""
    for d in DISCOVERY_DOMAINS:
        for q in d["questions"]:
            if q["id"] == question_id:
                return {**q, "domain_id": d["id"], "domain_title": d["title"]}
    return None


def get_all_question_ids():
    """Flat list of all question IDs (for validation)."""
    return [q["id"] for d in DISCOVERY_DOMAINS for q in d["questions"]]


def get_total_questions():
    """Total count of questions."""
    return sum(len(d["questions"]) for d in DISCOVERY_DOMAINS)


def get_domain_summary():
    """Return list of domain metadata WITHOUT questions (for dashboard)."""
    return [
        {
            "id": d["id"],
            "number": d["number"],
            "code": d["code"],
            "title": d["title"],
            "icon": d["icon"],
            "color": d["color"],
            "recommended_pic": d["recommended_pic"],
            "estimated_minutes": d["estimated_minutes"],
            "description": d["description"],
            "question_count": len(d["questions"]),
        }
        for d in DISCOVERY_DOMAINS
    ]


# ─── Branching / Conditional Visibility ──────────────────────────────────────
#
# Question dapat punya field `show_if` dengan struktur:
#   {"question_id": "D06-Q02", "operator": "equals|not_equals|in|not_in|includes|not_includes|is_truthy|is_falsy",
#    "values": [...]} atau "value": ...
#
# Logika DEFAULT-SHOW: jika dependensi BELUM dijawab → tampilkan (supaya user
# bisa eksplorasi). HIDE hanya jika dependensi sudah dijawab DAN kondisi tidak
# terpenuhi.
#
def evaluate_show_if(show_if, answers_map):
    """Return True kalau pertanyaan harus ditampilkan.

    `answers_map` = dict {question_id: {value, skipped, ...}}.
    """
    if not show_if:
        return True
    target_qid = show_if.get("question_id")
    if not target_qid:
        return True
    ans = (answers_map or {}).get(target_qid)
    # Default-show: kalau dependensi belum dijawab/di-skip, tampilkan
    if not ans or ans.get("skipped"):
        return True
    actual = ans.get("value")
    if actual is None or actual == "" or (isinstance(actual, list) and len(actual) == 0):
        return True

    operator = (show_if.get("operator") or "equals").lower()
    expected_single = show_if.get("value")
    expected_list = show_if.get("values") or []

    def _ensure_list(x):
        return x if isinstance(x, list) else [x]

    if operator == "equals":
        return actual == expected_single
    if operator == "not_equals":
        return actual != expected_single
    if operator == "in":
        return actual in expected_list
    if operator == "not_in":
        return actual not in expected_list
    if operator == "includes":
        # actual diharapkan list (multi_choice); bertemu jika ada irisan
        return any(v in _ensure_list(actual) for v in expected_list)
    if operator == "not_includes":
        return not any(v in _ensure_list(actual) for v in expected_list)
    if operator == "is_truthy":
        return bool(actual)
    if operator == "is_falsy":
        return not bool(actual)
    # Unknown operator → safe default: show
    return True


def filter_visible_questions(domain, answers_map):
    """Return list of questions in `domain` yang visible berdasarkan branching."""
    return [q for q in domain["questions"] if evaluate_show_if(q.get("show_if"), answers_map)]


def is_answer_filled(answer):
    """True kalau jawaban dianggap terisi (untuk perhitungan progress).

    Catatan (field `note`) saja TIDAK dihitung sebagai terisi — note bersifat
    pelengkap. Opsi "Lainnya" hanya dihitung terisi jika `other_text` diisi.
    """
    if not answer or answer.get("skipped"):
        return False
    value = answer.get("value")
    raw_other = answer.get("other_text")
    other_filled = bool(raw_other.strip()) if isinstance(raw_other, str) else bool(raw_other)

    if isinstance(value, list):
        if not value:
            return False
        non_sentinel = [v for v in value if v != OTHER_SENTINEL]
        if non_sentinel:
            return True
        return other_filled  # hanya "Lainnya" yang dipilih → butuh teks
    if value == OTHER_SENTINEL:
        return other_filled
    if value is None or value == "":
        return False
    return True


def count_visible_questions_per_domain(answers_map):
    """Return {domain_id: visible_count}."""
    out = {}
    for d in DISCOVERY_DOMAINS:
        out[d["id"]] = len(filter_visible_questions(d, answers_map))
    return out
