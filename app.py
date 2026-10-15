import json
from datetime import datetime

import pandas as pd
import streamlit as st

from monitors import run_monitor, OK, WARNING, FAIL
from vitals import LIMITS, next_reading, evaluate, overall

st.set_page_config(page_title="Health Monitor", page_icon="🏥", layout="wide")

ICONS = {OK: "🟢", WARNING: "🟠", FAIL: "🔴"}

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

for key in ("history", "vitals_history"):
    if key not in st.session_state:
        st.session_state[key] = []
if "last_reading" not in st.session_state:
    st.session_state.last_reading = {}

st.title("🏥 Monitorización sanitaria")

with st.sidebar:
    st.header("Ajustes")
    auto = st.toggle("Auto-refresco", value=True)
    interval = st.slider("Intervalo (s)", 2, 120, 5)
    st.button("Comprobar ahora")
    st.divider()
    st.caption("Rangos de alerta (aviso / fallo)")
    for k, (wl, wh, fl, fh, unit, label) in LIMITS.items():
        st.caption(f"**{label}**: aviso <{wl} o >{wh} · fallo <{fl} o >{fh} {unit}")


def run_all():
    rows = []
    now = datetime.now()
    for m in config["monitors"]:
        status, msg, value = run_monitor(m)
        rows.append({"Hora": now, "Monitor": m["name"], "Tipo": m["type"],
                     "Estado": status, "Detalle": msg, "Valor": value,
                     "Crítico": m.get("critical", False)})
    st.session_state.history.extend(rows)
    st.session_state.history = st.session_state.history[-2000:]
    return rows


def read_patients():
    now = datetime.now()
    current = []
    for p in config.get("patients", []):
        r = next_reading(st.session_state.last_reading.get(p["id"]))
        st.session_state.last_reading[p["id"]] = r
        current.append((p, r))
        st.session_state.vitals_history.append(
            {"Hora": now, "Paciente": p["name"], "FC": r["hr"], "Sistólica": r["sys"],
             "Diastólica": r["dia"], "SpO2": r["spo2"], "Estado": overall(r)})
    st.session_state.vitals_history = st.session_state.vitals_history[-3000:]
    return current


def systems_tab():
    df = pd.DataFrame(run_all())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("🟢 OK", int((df.Estado == OK).sum()))
    c3.metric("🟠 Warning", int((df.Estado == WARNING).sum()))
    c4.metric("🔴 Fail", int((df.Estado == FAIL).sum()))

    crit = df[(df.Estado == FAIL) & df["Crítico"]]
    if not crit.empty:
        st.error("🚨 Fallo en servicios críticos: " + ", ".join(crit.Monitor))

    for _, r in df.iterrows():
        st.markdown(f"{ICONS[r.Estado]} **{r.Monitor}** — {r.Estado} · {r.Detalle}")

    hist = pd.DataFrame(st.session_state.history)
    sel = st.selectbox("Monitor", hist.Monitor.unique(), key="sel_monitor")
    h = hist[(hist.Monitor == sel) & hist.Valor.notna()].set_index("Hora")
    if not h.empty:
        st.line_chart(h["Valor"])
    st.dataframe(hist[hist.Estado != OK].tail(50).sort_values("Hora", ascending=False),
                 use_container_width=True)


def patients_tab():
    current = read_patients()

    alarms = [f"{p['name']} ({p['bed']})" for p, r in current if overall(r) == FAIL]
    if alarms:
        st.error("🚨 Constantes en rango crítico: " + ", ".join(alarms))

    for p, r in current:
        with st.container(border=True):
            st.markdown(f"### {ICONS[overall(r)]} {p['name']} · {p['bed']}")
            cols = st.columns(4)
            for col, k in zip(cols, ("hr", "sys", "dia", "spo2")):
                unit, label = LIMITS[k][4], LIMITS[k][5]
                col.metric(f"{ICONS[evaluate(k, r[k])]} {label}", f"{r[k]:.0f} {unit}")
            st.caption(f"Tensión arterial: **{r['sys']:.0f}/{r['dia']:.0f} mmHg**")

    st.subheader("Tendencias")
    vh = pd.DataFrame(st.session_state.vitals_history)
    names = [p["name"] for p in config.get("patients", [])]
    sel = st.selectbox("Paciente", names, key="sel_patient")
    h = vh[vh.Paciente == sel].set_index("Hora")
    g1, g2, g3 = st.columns(3)
    g1.markdown("**Ritmo cardiaco (lpm)**")
    g1.line_chart(h[["FC"]])
    g2.markdown("**Tensión arterial (mmHg)**")
    g2.line_chart(h[["Sistólica", "Diastólica"]])
    g3.markdown("**Saturación O2 (%)**")
    g3.line_chart(h[["SpO2"]])

    with st.expander("Alertas recientes"):
        alerts = vh[vh.Estado != OK].tail(50).sort_values("Hora", ascending=False)
        st.dataframe(alerts, use_container_width=True)


@st.fragment(run_every=interval if auto else None)
def dashboard():
    tab_p, tab_s = st.tabs(["❤️ Pacientes", "🖥️ Sistemas"])
    with tab_p:
        patients_tab()
    with tab_s:
        systems_tab()
    st.caption(f"Última comprobación: {datetime.now():%H:%M:%S}")


dashboard()
