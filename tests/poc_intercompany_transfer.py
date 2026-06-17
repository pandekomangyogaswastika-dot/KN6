"""POC — Sub-fase 1.5 Inter-Company Transfer Flow (KN_15 §7).

Membuktikan alur nyata B→E:
  1. Preview: Kanda jual Batik 100 → mode inter_company (KSC punya stok).
  2. Buat transfer inter-company (source=KSC, dest=Kanda, Batik 100) → status waiting_approval, roll KSC ter-reserve.
  3. KSC available turun 100 (ter-reserve utk transfer).
  4. Approve → ownership pindah KSC→Kanda, status completed.
  5. Kanda kini punya 100 available Batik; KSC berkurang 100.
  6. Preview ulang: Kanda Batik 100 → kini from_stock.
  7. Konservasi: total available Batik (semua entitas) tetap (hanya owner pindah).
"""
import sys
import httpx

BASE = "http://localhost:8001/api"
ADMIN = {"email": "admin@kainnusantara.id", "password": "demo12345"}


def login(c):
    r = c.post(f"{BASE}/auth/login", json=ADMIN); r.raise_for_status()
    c.headers["Authorization"] = f"Bearer {r.json()['token']}"


def find_product(products, needle):
    for p in products:
        if needle.lower() in p["name"].lower():
            return p
    raise RuntimeError(f"produk '{needle}' tak ada")


def preview(c, entity_id, pid, qty):
    r = c.post(f"{BASE}/sales-orders/preview-allocation", json={
        "entity_id": entity_id, "items": [{"product_id": pid, "quantity": qty, "unit": "meter"}]})
    r.raise_for_status()
    return r.json()["lines"][0]


def avail_for(c, pid, entity_id):
    """Total available produk utk entitas tertentu via status-board."""
    rows = c.get(f"{BASE}/inventory/status-board", params={"product_id": pid}).json()
    if not rows:
        return 0.0, 0.0
    row = rows[0]
    own = 0.0
    for e in row["by_entity"]:
        if e["entity_id"] == entity_id:
            own = e["available"]
    return own, row["total_available"]


def main():
    fails = []
    with httpx.Client(timeout=40) as c:
        login(c)
        ents = {e["short_name"]: e["id"] for e in c.get(f"{BASE}/entities").json()}
        ksc, kanda = ents["KSC"], ents["Kanda"]
        prods = c.get(f"{BASE}/products").json()
        batik = find_product(prods, "Batik Mega")["id"]
        QTY = 60.0

        # 1. preview Kanda → inter_company
        ln = preview(c, kanda, batik, QTY)
        print(f"1. Kanda Batik {QTY} → mode={ln['primary_mode']} (cross={[x['entity_name'] for x in ln['cross_entity']]})")
        if ln["primary_mode"] != "inter_company":
            fails.append("step1_not_inter_company")

        ksc_before, total_before = avail_for(c, batik, ksc)
        kanda_before, _ = avail_for(c, batik, kanda)
        print(f"   before: KSC avail={ksc_before}, Kanda avail={kanda_before}, total={total_before}")

        # 2. create inter-company transfer
        r = c.post(f"{BASE}/transfers/inter-company", json={
            "source_entity_id": ksc, "dest_entity_id": kanda,
            "items": [{"product_id": batik, "quantity": QTY, "unit": "meter"}],
            "notes": "POC inter-company", "requested_by": "POC"})
        r.raise_for_status()
        trf = r.json()
        print(f"2. transfer created: {trf['code']} kind={trf['transfer_kind']} status={trf['status']} "
              f"rolls={sum(len(i['rolls']) for i in trf['items'])}")
        if trf["status"] != "waiting_approval" or trf["transfer_kind"] != "inter_entity":
            fails.append("step2_bad_transfer")

        # 3. KSC available turun (ter-reserve)
        ksc_pending, _ = avail_for(c, batik, ksc)
        print(f"3. KSC avail setelah request = {ksc_pending} (harus turun {QTY} dari {ksc_before})")
        if abs(ksc_pending - (ksc_before - QTY)) > 0.5:
            fails.append("step3_reserve_not_applied")

        # 4. approve → ownership move
        r = c.post(f"{BASE}/transfers/{trf['id']}/approve", json={"approved_by": "Manager KSC"})
        r.raise_for_status()
        appr = r.json()
        print(f"4. approve → status={appr['status']} moved={appr.get('ownership_moved')}")
        if appr["status"] != "completed":
            fails.append("step4_not_completed")

        # 5. Kanda kini punya stok
        ksc_after, total_after = avail_for(c, batik, ksc)
        kanda_after, _ = avail_for(c, batik, kanda)
        print(f"5. after: KSC avail={ksc_after}, Kanda avail={kanda_after}, total={total_after}")
        if abs(kanda_after - (kanda_before + QTY)) > 0.5:
            fails.append("step5_kanda_no_stock")
        if abs(ksc_after - (ksc_before - QTY)) > 0.5:
            fails.append("step5_ksc_not_reduced")

        # 6. preview ulang Kanda → from_stock
        ln2 = preview(c, kanda, batik, QTY)
        print(f"6. Kanda Batik {QTY} (ulang) → mode={ln2['primary_mode']}")
        if ln2["primary_mode"] != "from_stock":
            fails.append("step6_not_from_stock")

        # 7. konservasi total available
        print(f"7. konservasi total: before={total_before} after={total_after}")
        if abs(total_after - total_before) > 0.5:
            fails.append("step7_total_changed")

    print("\n" + ("✅ SEMUA POC 1.5 LULUS" if not fails else f"❌ GAGAL: {fails}"))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
