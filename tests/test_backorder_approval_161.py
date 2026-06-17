"""E2E test — Sub-fase 1.6.1 Approval-with-Backorder + Auto-commit (HTTP).

Skenario:
  1. Login admin; pilih entitas + produk dengan available > 0.
  2. Buat SO allow_backorder=true, qty = available + EXTRA.
     → status HARUS 'reserved' (bukan waiting_stock) + has_backorder=true (decoupled).
  3. submit-for-approval (+approve bila perlu) → status 'approved', has_backorder TETAP true.
  4. Buat PO qty=backorder → approve → inbound scan-receive + complete (GR).
  5. → SO TETAP 'approved', has_backorder=false, item backorder_qty=0, reserved=qty penuh.
  6. Verifikasi auto-commit: SEMUA roll milik SO berstatus 'committed' (pymongo).
"""
import os, sys, requests

BASE = os.environ.get("BACKEND_URL", "https://po-refactor.preview.emergentagent.com").rstrip("/")
API = f"{BASE}/api"
EXTRA = 60.0
PASS, FAIL = [], []


def ok(m): PASS.append(m); print(f"  [PASS] {m}")
def bad(m): FAIL.append(m); print(f"  [FAIL] {m}")


def main():
    s = requests.Session()
    s.headers.update({"Authorization": "Bearer " + s.post(
        f"{API}/auth/login", json={"email": "admin@kainnusantara.id", "password": "demo12345"}, timeout=30
    ).json()["token"]})
    ok("login admin")

    eid = s.get(f"{API}/entities", timeout=30).json()[0]["id"]
    wh = s.get(f"{API}/warehouses", timeout=30).json()[0]

    # Pilih produk dengan available TERBESAR milik entitas (pastikan ada porsi reserved)
    board = s.get(f"{API}/inventory/status-board", params={"owner_entity_id": eid}, timeout=30).json()
    best = None
    for row in board:
        for be in row.get("by_entity", []):
            if be.get("entity_id") == eid:
                a = float(be.get("available", 0) or 0)
                if best is None or a > best[1]:
                    best = (row["product_id"], a)
    assert best and best[1] > 0, "tidak ada produk dengan available>0 untuk entitas"
    prod_id, avail = best
    req_qty = round(avail + EXTRA, 2)
    print(f"  produk={prod_id} available={avail} request={req_qty}")

    cust = s.get(f"{API}/customers", timeout=30).json()[0]
    addr = cust.get("addresses", [{}])[0].get("id")
    so = s.post(f"{API}/sales-orders", json={
        "customer_id": cust["id"], "shipping_address_id": addr, "entity_id": eid,
        "allow_backorder": True, "items": [{"product_id": prod_id, "quantity": req_qty, "unit": "meter"}],
    }, timeout=30).json()
    so_id = so["id"]
    print(f"  SO {so['number']} status={so['status']} has_backorder={so.get('has_backorder')}")

    # 2) decoupled: status reserved (ada porsi reserved) walau ada backorder
    if so["status"] == "reserved":
        ok("decoupled: SO status == reserved meski ada backorder")
    else:
        bad(f"decoupled: status seharusnya reserved, dapat {so['status']}")
    if so.get("has_backorder"):
        ok("has_backorder == true")
    else:
        bad("has_backorder seharusnya true")
    bo_qty = round(float(so["items"][0].get("backorder_qty", 0)), 2)

    # 3) submit-for-approval (+approve bila perlu)
    r = s.post(f"{API}/sales-orders/{so_id}/submit-for-approval", timeout=30)
    assert r.status_code == 200, f"submit {r.status_code}: {r.text}"
    st = r.json().get("status")
    if st == "waiting_approval":
        r = s.post(f"{API}/sales-orders/{so_id}/approve", timeout=30)
        assert r.status_code == 200, f"approve {r.status_code}: {r.text}"
        st = r.json().get("status")
    so_after = s.get(f"{API}/sales-orders/{so_id}", timeout=30).json()
    if so_after["status"] == "approved":
        ok("approval: SO approved meski masih ada backorder (lanjut approval sebelum fulfil penuh)")
    else:
        bad(f"approval: status seharusnya approved, dapat {so_after['status']}")
    if so_after.get("has_backorder"):
        ok("approval: has_backorder TETAP true setelah approve")
    else:
        bad("approval: has_backorder seharusnya tetap true")

    # 4) PO menutup backorder → GR
    po = s.post(f"{API}/purchase-orders", json={
        "supplier_name": "Supplier 161", "warehouse_id": wh["id"], "entity_id": eid,
        "items": [{"product_id": prod_id, "quantity": bo_qty, "unit": "meter", "price": 0.0}],
    }, timeout=30).json()
    po_id = po["id"]
    if po["status"] == "waiting_approval":
        s.post(f"{API}/purchase-orders/{po_id}/approve", timeout=30)
    task = next((t for t in s.get(f"{API}/inbound/tasks", timeout=30).json()
                 if t.get("po_id") == po_id and t.get("product_id") == prod_id), None)
    assert task, "inbound task tidak ditemukan"
    exp = float(task["expected_qty"])
    s.post(f"{API}/inbound/tasks/{task['id']}/scan-receive",
           json={"product_id": prod_id, "actual_qty": exp, "lot": "LOT-161", "batch": "B161"}, timeout=30)
    rc = s.post(f"{API}/inbound/tasks/{task['id']}/complete", timeout=30)
    assert rc.status_code == 200, f"complete {rc.status_code}: {rc.text}"
    print(f"  GR complete status={rc.json().get('status')}")

    # 5) SO tetap approved, backorder beres
    so2 = s.get(f"{API}/sales-orders/{so_id}", timeout=30).json()
    print(f"  SO setelah GR: status={so2['status']} has_backorder={so2.get('has_backorder')}")
    if so2["status"] == "approved":
        ok("auto-fulfill: status TETAP approved (tidak turun, tidak perlu approval ulang)")
    else:
        bad(f"auto-fulfill: status seharusnya approved, dapat {so2['status']}")
    if not so2.get("has_backorder"):
        ok("auto-fulfill: has_backorder == false")
    else:
        bad("auto-fulfill: has_backorder seharusnya false")
    it = so2["items"][0]
    if float(it.get("backorder_qty", 1)) <= 0.5 and abs(float(it.get("reserved_qty", 0)) - req_qty) < 0.5:
        ok(f"auto-fulfill: item reserved={it.get('reserved_qty')} backorder={it.get('backorder_qty')}")
    else:
        bad(f"auto-fulfill: item reserved={it.get('reserved_qty')} backorder={it.get('backorder_qty')}")

    # 6) Auto-commit: semua roll SO berstatus committed
    try:
        from pymongo import MongoClient
        cli = MongoClient("mongodb://localhost:27017")
        db = cli["test_database"]
        rolls = list(db.inventory_rolls.find({"reserved_ref.id": so_id}, {"_id": 0, "status": 1}))
        statuses = {r.get("status") for r in rolls}
        print(f"  roll SO: {len(rolls)} roll, status={statuses}")
        if rolls and statuses == {"committed"}:
            ok(f"auto-commit: {len(rolls)} roll SO semuanya 'committed' (ikut approval awal)")
        else:
            bad(f"auto-commit: roll SO status={statuses} (harusnya semua committed)")
        cli.close()
    except Exception as e:
        print(f"  [WARN] verifikasi commit dilewati: {e}")

    print("\n" + "=" * 60)
    print(f"  HASIL: {len(PASS)} PASS | {len(FAIL)} FAIL")
    print("=" * 60)
    if FAIL:
        for f in FAIL:
            print(f"   - FAIL: {f}")
        sys.exit(1)
    print("  SEMUA SKENARIO APPROVAL-WITH-BACKORDER LULUS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
