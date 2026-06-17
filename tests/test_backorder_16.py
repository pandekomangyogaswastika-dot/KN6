"""E2E test — Sub-fase 1.6 Backorder Lifecycle (HTTP, against running backend).

Skenario:
  1. Login admin.
  2. Pilih entitas penjual + produk, baca available milik entitas (status-board).
  3. Buat SO dengan allow_backorder=true, qty = available + EXTRA → paksa backorder.
     Verifikasi: status=waiting_stock, has_backorder, reserved+backorder==qty.
  4. Buat PO produk+entitas+gudang qty = backorder, approve bila perlu → inbound task.
  5. scan-receive penuh → complete (GR) → roll dibuat + auto-fulfill.
  6. Verifikasi SO: status=reserved, backorder fulfilled (backorder_qty==0).
"""
import os, sys, requests

BASE = os.environ.get("BACKEND_URL", "https://po-refactor.preview.emergentagent.com").rstrip("/")
API = f"{BASE}/api"
EXTRA = 50.0  # qty backorder yang dipaksa
PASS, FAIL = [], []


def ok(msg):
    PASS.append(msg); print(f"  [PASS] {msg}")


def bad(msg):
    FAIL.append(msg); print(f"  [FAIL] {msg}")


def main():
    s = requests.Session()
    # 1) Login
    r = s.post(f"{API}/auth/login", json={"email": "admin@kainnusantara.id", "password": "demo12345"}, timeout=30)
    assert r.status_code == 200, f"login {r.status_code}: {r.text}"
    token = r.json()["token"]
    s.headers.update({"Authorization": f"Bearer {token}"})
    ok("login admin")

    entities = s.get(f"{API}/entities", timeout=30).json()
    entity = entities[0]
    eid = entity["id"]
    print(f"  entity penjual: {entity.get('short_name', eid)} ({eid})")

    warehouses = s.get(f"{API}/warehouses", timeout=30).json()
    wh = warehouses[0]
    print(f"  gudang PO: {wh.get('name')} ({wh.get('city')})")

    # 2) Pilih produk + baca available milik entitas via status-board
    board = s.get(f"{API}/inventory/status-board", params={"owner_entity_id": eid}, timeout=30).json()
    prod_id, avail = None, 0.0
    for row in board:
        for be in row.get("by_entity", []):
            if be.get("entity_id") == eid:
                prod_id = row["product_id"]; avail = float(be.get("available", 0) or 0)
                break
        if prod_id:
            break
    if not prod_id:
        # fallback: produk pertama, available 0
        prods = s.get(f"{API}/products", timeout=30).json()
        prod_id, avail = prods[0]["id"], 0.0
    req_qty = round(avail + EXTRA, 2)
    print(f"  produk={prod_id} available(entitas)={avail} request={req_qty} → backorder≈{EXTRA}")

    # 3) Customer + alamat
    customers = s.get(f"{API}/customers", timeout=30).json()
    cust = customers[0]
    addr_id = cust.get("addresses", [{}])[0].get("id")

    so_payload = {
        "customer_id": cust["id"],
        "shipping_address_id": addr_id,
        "entity_id": eid,
        "allow_backorder": True,
        "items": [{"product_id": prod_id, "quantity": req_qty, "unit": "meter"}],
    }
    r = s.post(f"{API}/sales-orders", json=so_payload, timeout=30)
    assert r.status_code == 200, f"create SO {r.status_code}: {r.text}"
    so = r.json()
    so_id = so["id"]
    print(f"  SO dibuat: {so['number']} status={so['status']}")

    if so["status"] == "waiting_stock":
        ok("SO status == waiting_stock")
    else:
        bad(f"SO status seharusnya waiting_stock, dapat {so['status']}")
    if so.get("has_backorder"):
        ok("SO.has_backorder == true")
    else:
        bad("SO.has_backorder seharusnya true")
    item = so["items"][0]
    rq, bq = float(item.get("reserved_qty", 0)), float(item.get("backorder_qty", 0))
    if abs((rq + bq) - req_qty) < 0.5:
        ok(f"item: reserved({rq}) + backorder({bq}) == quantity({req_qty})")
    else:
        bad(f"item: reserved({rq}) + backorder({bq}) != quantity({req_qty})")
    bo_qty = round(bq, 2)
    if bo_qty <= 0.5:
        bad(f"backorder_qty tidak terbentuk ({bo_qty})")
        summary(); return

    # 4) PO untuk menutup backorder (price 0 → minim approval)
    po_payload = {
        "supplier_name": "Supplier Test 1.6",
        "warehouse_id": wh["id"],
        "entity_id": eid,
        "items": [{"product_id": prod_id, "quantity": bo_qty, "unit": "meter", "price": 0.0}],
    }
    r = s.post(f"{API}/purchase-orders", json=po_payload, timeout=30)
    assert r.status_code == 200, f"create PO {r.status_code}: {r.text}"
    po = r.json()
    po_id = po["id"]
    print(f"  PO dibuat: {po['po_number']} status={po['status']}")
    if po["status"] == "waiting_approval":
        r = s.post(f"{API}/purchase-orders/{po_id}/approve", timeout=30)
        assert r.status_code == 200, f"approve PO {r.status_code}: {r.text}"
        print("  PO di-approve → inbound task dibuat")

    # 5) Temukan inbound task untuk PO ini
    tasks = s.get(f"{API}/inbound/tasks", timeout=30).json()
    task = next((t for t in tasks if t.get("po_id") == po_id and t.get("product_id") == prod_id), None)
    assert task, "inbound task tidak ditemukan untuk PO"
    tid = task["id"]
    exp = float(task["expected_qty"])
    print(f"  inbound task {tid} expected={exp} status={task['status']}")

    # scan-receive penuh
    r = s.post(f"{API}/inbound/tasks/{tid}/scan-receive",
               json={"product_id": prod_id, "actual_qty": exp, "lot": "LOT-TEST16", "batch": "B16"}, timeout=30)
    assert r.status_code == 200, f"scan-receive {r.status_code}: {r.text}"
    # complete (GR) → roll + auto-fulfill
    r = s.post(f"{API}/inbound/tasks/{tid}/complete", timeout=30)
    assert r.status_code == 200, f"complete {r.status_code}: {r.text}"
    print(f"  GR complete → status={r.json().get('status')}")

    # 6) Verifikasi SO ter-auto-fulfill
    so2 = s.get(f"{API}/sales-orders/{so_id}", timeout=30).json()
    print(f"  SO setelah GR: status={so2['status']} has_backorder={so2.get('has_backorder')}")
    if so2["status"] == "reserved":
        ok("auto-fulfill: SO status kembali ke reserved")
    else:
        bad(f"auto-fulfill: SO status seharusnya reserved, dapat {so2['status']}")
    if not so2.get("has_backorder"):
        ok("auto-fulfill: has_backorder == false")
    else:
        bad("auto-fulfill: has_backorder seharusnya false")
    it2 = so2["items"][0]
    if float(it2.get("backorder_qty", 1)) <= 0.5 and abs(float(it2.get("reserved_qty", 0)) - req_qty) < 0.5:
        ok(f"auto-fulfill: item reserved={it2.get('reserved_qty')} backorder={it2.get('backorder_qty')}")
    else:
        bad(f"auto-fulfill: item reserved={it2.get('reserved_qty')} backorder={it2.get('backorder_qty')}")

    summary()


def summary():
    print("\n" + "=" * 60)
    print(f"  HASIL: {len(PASS)} PASS | {len(FAIL)} FAIL")
    print("=" * 60)
    if FAIL:
        for f in FAIL:
            print(f"   - FAIL: {f}")
        sys.exit(1)
    print("  SEMUA SKENARIO BACKORDER LULUS.")
    sys.exit(0)


if __name__ == "__main__":
    main()
