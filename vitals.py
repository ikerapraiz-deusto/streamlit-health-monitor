"""Constantes vitales: frecuencia cardiaca, tensión arterial y saturación de oxígeno.

Las lecturas son SIMULADAS (paseo aleatorio). Sustituir `next_reading`
por una integración real (HL7, FHIR, API del monitor de paciente...).
"""
import random

from monitors import OK, WARNING, FAIL

# (aviso_bajo, aviso_alto, fallo_bajo, fallo_alto, unidad, etiqueta)
LIMITS = {
    "hr":   (50, 110, 40, 130, "lpm",  "Ritmo cardiaco"),
    "sys":  (95, 140, 85, 180, "mmHg", "Tensión sistólica"),
    "dia":  (60, 90, 50, 110, "mmHg", "Tensión diastólica"),
    "spo2": (94, 101, 90, 101, "%",    "Saturación O2"),
}

BASE = {"hr": 75, "sys": 120, "dia": 80, "spo2": 97}
STEP = {"hr": 4, "sys": 5, "dia": 3, "spo2": 0.8}
RANGE = {"hr": (30, 170), "sys": (60, 220), "dia": (35, 130), "spo2": (70, 100)}


def next_reading(prev=None):
    """Genera la siguiente lectura a partir de la anterior (con vuelta a la media)."""
    prev = prev or BASE
    out = {}
    for k in BASE:
        v = prev[k] + (BASE[k] - prev[k]) * 0.1 + random.gauss(0, STEP[k])
        lo, hi = RANGE[k]
        out[k] = round(max(lo, min(hi, v)), 1)
    # la diastólica siempre menor que la sistólica
    if out["dia"] >= out["sys"] - 15:
        out["dia"] = round(out["sys"] - 15, 1)
    return out


def evaluate(key, value):
    wl, wh, fl, fh, _, _ = LIMITS[key]
    if value < fl or value > fh:
        return FAIL
    if value < wl or value > wh:
        return WARNING
    return OK


def overall(reading):
    states = [evaluate(k, reading[k]) for k in LIMITS]
    if FAIL in states:
        return FAIL
    if WARNING in states:
        return WARNING
    return OK
