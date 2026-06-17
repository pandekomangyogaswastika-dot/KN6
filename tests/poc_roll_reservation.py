"""POC core test (Fase 0.5) — Roll-as-SSOT reservation lifecycle via API.

Membuktikan: create SO → reservasi LEVEL ROLL (owner-scoped, split) → approve
(commit) → cancel/release → roll kembali available + balance konsisten. Tidak
ada stok hilang/tercipta (konservasi).
"""
import asyncio, os, sys
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("backend/.env")
API = "http://localhost:8001"
DB = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
G, R, X = "\033[92m", "\033[91m", "\033[0m"
results = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    if cond:
        results["pass"] += 1
        print(f"  {G}[PASS]{X} {name}")
    else:
        results["fail"] += 1
        print(f"  {R}[FAIL]{X} {name}  {detail}")


async def seg_totals(product_id, owner):
    rolls = await DB.inventory_rolls.find(
        {"product_id": product_id, "owner_entity_id": owner}, {"_id": 0}
    ).to_list(5000)
    avail = sum(float(r["length_remaining"]) for r in rolls if r["status"] == "available")
    res = sum(float(r["length_remaining"]) for r in rolls if r["status"] == "reserved")
    com = sum(float(r["length_remaining"]) for r in rolls if r["status"] == "committed")
    total = sum(float(r["length_remaining"]) for r in rolls)
    return round(avail, 2), round(res, 2), round(com, 2), round(total, 2)


async def main():
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{API}/api/auth/login",
                         json={"email": "admin@kainnusantara.id", "password": "demo12345"}, timeout=20)
        token = r.json().get("token")
        check("login admin", bool(token))
        h = {"Authorization": f"Bearer {token}"}

        # Pilih produk yang punya stok available milik ent_ksc
        prods = (await c.get(f"{API}/api/products", headers=h)).json()
        target = next((p for p in prods if float(p.get("available_qty", 0)) >= 40), None)
        check("ada produk dgn available>=40", target is not None)
        if not target:
            return
        pid = target["id"]
        owner = "ent_ksc"
        a0, r0, c0, t0 = await seg_totals(pid, owner)
        print(f"  [info] produk={target['name']} avail0={a0} reserved0={r0} committed0={c0} total0={t0}")

        # Customer + alamat
        custs = (await c.get(f"{API}/api/customers", headers=h)).json()
        cust = next((x for x in custs if x.get("addresses")), custs[0])
        addr_id = cust["addresses"][0]["id"]

        QTY = 37.0  # qty 'aneh' → uji split roll
        order_payload = {
            "customer_id": cust["id"], "shipping_address_id": addr_id,
            "items": [{"product_id": pid, "quantity": QTY, "unit": target.get("base_unit", "meter")}],
            "entity_id": owner,
        }
        ro = await c.post(f"{API}/api/sales-orders", headers=h, json=order_payload, timeout=30)
        check("create SO (reservasi roll)", ro.status_code == 200, ro.text[:200])
        order = ro.json()
        oid = order["id"]
        allocs = order.get("allocations", [])
        check("SO punya allocations dgn rolls", bool(allocs) and all(a.get("rolls") for a in allocs))
        check("alokasi owner-scoped (owner==entity)", all(a.get("owner_entity_id") == owner for a in allocs))
        reserved_len = sum(float(rr["length"]) for a in allocs for rr in a["rolls"])
        check("Σ reserved roll length == qty order (split exact)", abs(reserved_len - QTY) < 0.01,
              f"reserved={reserved_len} vs qty={QTY}")

        a1, r1, c1, t1 = await seg_totals(pid, owner)
        check("available turun tepat QTY", abs(a1 - (a0 - QTY)) < 0.01, f"{a1} vs {a0-QTY}")
        check("reserved naik tepat QTY", abs(r1 - (r0 + QTY)) < 0.01, f"{r1} vs {r0+QTY}")
        check("konservasi total (tidak ada stok hilang/tercipta)", abs(t1 - t0) < 0.01, f"{t1} vs {t0}")

        # Approve → commit roll
        ra = await c.post(f"{API}/api/sales-orders/{oid}/approve", headers=h, timeout=20)
        check("approve SO", ra.status_code == 200, ra.text[:150])
        a2, r2, c2, t2 = await seg_totals(pid, owner)
        check("setelah approve: committed naik tepat QTY", abs(c2 - (c0 + QTY)) < 0.01, f"{c2} vs {c0+QTY}")
        check("setelah approve: reserved kembali ke awal", abs(r2 - r0) < 0.01, f"{r2} vs {r0}")
        check("konservasi total tetap", abs(t2 - t0) < 0.01)

        # Cancel → release semua roll
        rc = await c.post(f"{API}/api/sales-orders/{oid}/cancel", headers=h, timeout=20)
        check("cancel SO", rc.status_code == 200, rc.text[:150])
        a3, r3, c3, t3 = await seg_totals(pid, owner)
        check("setelah cancel: available kembali ke awal", abs(a3 - a0) < 0.01, f"{a3} vs {a0}")
        check("setelah cancel: reserved+committed = 0 delta", abs(r3 - r0) < 0.01 and abs(c3 - c0) < 0.01)
        check("konservasi total tetap (akhir)", abs(t3 - t0) < 0.01)

        # Balance proyeksi == rolls (segmen) untuk produk ini
        bals = await DB.inventory_balances.find({"product_id": pid}, {"_id": 0}).to_list(100)
        seg_av = {}
        for w in await DB.inventory_rolls.find({"product_id": pid, "status": "available"}, {"_id": 0}).to_list(5000):
            key = (w["warehouse_id"], w["owner_entity_id"])
            seg_av[key] = seg_av.get(key, 0) + float(w["length_remaining"])
        ok = all(abs(float(b.get("available_qty", 0)) - round(seg_av.get((b["warehouse_id"], b["owner_entity_id"]), 0), 2)) < 0.5 for b in bals)
        check("balance.available == Σ rolls available (proyeksi konsisten)", ok)

    print(f"\n  TOTAL: {G}{results['pass']} PASS{X} | {R}{results['fail']} FAIL{X}")
    return 1 if results["fail"] else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
