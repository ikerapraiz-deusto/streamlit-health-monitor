import shutil
import socket
import random
import time
import requests

OK, WARNING, FAIL = "OK", "WARNING", "FAIL"


def check_http(m):
    t0 = time.time()
    try:
        r = requests.get(m["target"], timeout=5)
        ms = (time.time() - t0) * 1000
        if r.status_code >= 400:
            return FAIL, f"HTTP {r.status_code}", ms
        if ms > 1500:
            return WARNING, f"Lento: {ms:.0f} ms", ms
        return OK, f"HTTP {r.status_code} en {ms:.0f} ms", ms
    except Exception as e:
        return FAIL, str(e)[:80], None


def check_tcp(m):
    host, port = m["target"].rsplit(":", 1)
    t0 = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=5):
            ms = (time.time() - t0) * 1000
            return OK, f"Puerto {port} abierto ({ms:.0f} ms)", ms
    except Exception as e:
        return FAIL, str(e)[:80], None


def check_disk(m):
    u = shutil.disk_usage(m["target"])
    pct = u.used / u.total * 100
    if pct >= m.get("fail", 90):
        return FAIL, f"Uso {pct:.1f}%", pct
    if pct >= m.get("warn", 80):
        return WARNING, f"Uso {pct:.1f}%", pct
    return OK, f"Uso {pct:.1f}%", pct


def check_vitals(m):
    """Simula constantes de un monitor de paciente (sustituir por integración real)."""
    hr = random.gauss(75, 12)
    spo2 = min(100, random.gauss(96, 2))
    msg = f"FC {hr:.0f} lpm | SpO2 {spo2:.0f}%"
    if spo2 < 90 or hr > 130 or hr < 40:
        return FAIL, msg, hr
    if spo2 < 94 or hr > 110 or hr < 50:
        return WARNING, msg, hr
    return OK, msg, hr


CHECKS = {"http": check_http, "tcp": check_tcp, "disk": check_disk,
          "simulated_vitals": check_vitals}


def run_monitor(m):
    return CHECKS[m["type"]](m)
