"""POC — Sub-fase 1.4 ATP & Fulfillment Modes (verifikasi endpoint nyata).

Membuktikan classifier menghasilkan 4 mode benar di atas data seed:
  - from_stock     : KSC jual Batik 100 (avail 755)
  - from_incoming  : KSC jual Ulos 300 (avail 235 + incoming 100 = ATP 335)
  - backorder      : KSC jual Ulos 400 (ATP 335 < 400 → backorder 65)
  - inter_company  : Kanda jual Batik 100 (Kanda 0, KSC 755 → peluang transfer)
Juga memeriksa Inventory Status Board (cross-entity indicator).
"""
import sys
import httpx

BASE = "http://localhost:8001/api"
ADMIN = {"email": "admin@kainnusantara.id", "password": "demo12345"}


def login(c):
    r = c.post(f"{BASE}/auth/login", json=ADMIN)
    r.raise_for_status()
    tok = r.json()["token"]
    c.headers["Authorization"] = f"Bearer {tok}"


def find_product(products, needle):
    for p in products:
        if needle.lower() in p["name"].lower():
            return p["id"]
    raise RuntimeError(f"produk '{needle}' tidak ditemukan")


def preview(c, entity_id, product_id, qty):
    r = c.post(f"{BASE}/sales-orders/preview-allocation", json={
        "entity_id": entity_id,
        "items": [{"product_id": product_id, "quantity": qty, "unit": "meter"}],
    })
    r.raise_for_status()
    return r.json()["lines"][0]


def main():
    fails = []
    with httpx.Client(timeout=30) as c:
        login(c)
        ents = {e["short_name"]: e["id"] for e in c.get(f"{BASE}/entities").json()}
        ksc, kanda = ents.get("KSC"), ents.get("Kanda")
        products = c.get(f"{BASE}/products").json()
        batik = find_product(products, "Batik Mega")
        ulos = find_product(products, "Ulos")
        jumputan = find_product(products, "Jumputan")

        cases = [
            ("from_stock",    ksc,   batik, 100, "from_stock"),
            ("from_incoming", ksc,   ulos,  300, "from_incoming"),
            ("backorder",     ksc,   ulos,  400, "backorder"),
            ("inter_company", kanda, batik, 100, "inter_company"),
            ("from_incoming(Kanda)", kanda, jumputan, 100, "from_incoming"),
        ]
        for label, eid, pid, qty, expect in cases:
            ln = preview(c, eid, pid, qty)
            mode = ln["primary_mode"]
            ok = mode == expect
            bd = ln["breakdown"]
            print(f"[{'OK ' if ok else 'FAIL'}] {label:<22} qty={qty} → mode={mode} "
                  f"(exp {expect}) | avail={ln['own_available']} inc={ln['own_incoming']} "
                  f"atp={ln['own_atp']} other={ln['other_entity_available']} "
                  f"bd={bd} cross={[x['entity_name'] for x in ln['cross_entity']]}")
            if not ok:
                fails.append(label)

        # Status board
        board = c.get(f"{BASE}/inventory/status-board").json()
        print(f"\n[INFO] Status board rows: {len(board)}")
        inter = [r for r in board if r["has_intercompany_opportunity"]]
        sample = board[0] if board else {}
        print(f"[INFO] inter-company opportunities: {len(inter)} produk")
        print(f"[INFO] sample row: {sample.get('product_name')} on_hand={sample.get('total_on_hand')} "
              f"avail={sample.get('total_available')} reserved={sample.get('total_reserved')} "
              f"incoming={sample.get('total_incoming')} atp={sample.get('total_atp')} "
              f"entities={[e['entity_name'] for e in sample.get('by_entity', [])]}")
        if len(board) < 1:
            fails.append("status_board_empty")
        # ATP konsistensi: total_atp == total_available + total_incoming
        for r in board:
            if abs(r["total_atp"] - (r["total_available"] + r["total_incoming"])) > 0.05:
                fails.append(f"atp_mismatch:{r['sku']}")

    print("\n" + ("✅ SEMUA POC LULUS" if not fails else f"❌ GAGAL: {fails}"))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
