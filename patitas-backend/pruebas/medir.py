"""Mide tiempos de /api/animales/cercanos/ con 1, 10 y 50 usuarios simultáneos.
Uso: python pruebas/medir.py [URL_BASE]   (por defecto http://127.0.0.1:8000)"""
import sys, time, statistics, threading, urllib.request
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
URL = BASE + "/api/animales/cercanos/?lat=4.7059&lng=-74.2309&radio=5000"
def uno(res):
    t = time.perf_counter()
    try: ok = urllib.request.urlopen(URL, timeout=120).status == 200
    except Exception: ok = False
    res.append((ok, (time.perf_counter() - t) * 1000))
def escenario(users, total):
    res = []; sem = threading.Semaphore(users); hs = []
    def w():
        with sem: uno(res)
    for _ in range(total):
        h = threading.Thread(target=w); h.start(); hs.append(h)
    for h in hs: h.join()
    t = sorted(x[1] for x in res)
    print(f"{users:>3} usuarios | n={total:<4} ok={sum(x[0] for x in res):<4} "
          f"media={statistics.mean(t):8.1f} p95={t[max(int(len(t)*0.95)-1,0)]:8.1f} max={t[-1]:8.1f}  (ms)")
urllib.request.urlopen(URL, timeout=60)  # calentamiento
for u, n in ((1, 50), (10, 100), (50, 200)): escenario(u, n)
