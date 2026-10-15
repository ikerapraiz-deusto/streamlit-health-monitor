import json
from datetime import datetime

import pandas as pd
import streamlit as st

from monitors import run_monitor, OK, WARNING, FAIL

st.set_page_config(page_title="Health Monitor", page_icon="🏥", layout="wide")

ICONS = {OK: "🟢", WARNING: "🟠", FAIL: "🔴"}

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🏥 Monitorización de sistemas sanitarios")

with st.sidebar:
    st.header("Ajustes")
    auto = st.toggle("Auto-refresco", value=True)
    interval = st.slider("Intervalo (s)", 5, 120, 15)
    st.button("Comprobar ahora")


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


@st.fragment(run_every=interval if auto else None)
def dashboard():
    rows = run_all()
    df = pd.DataFrame(rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("🟢 OK", (df.Estado == OK).sum())
    c3.metric("🟠 Warning", (df.Estado == WARNING).sum())
    c4.metric("🔴 Fail", (df.Estado == FAIL).sum())

    crit = df[(df.Estado == FAIL) & df["Crítico"]]
    if not crit.empty:
        st.error("🚨 Fallo en servicios críticos: " + ", ".join(crit.Monitor))

    st.subheader("Estado actual")
    for _, r in df.iterrows():
        st.markdown(f"{ICONS[r.Estado]} **{r.Monitor}** — {r.Estado} · {r.Detalle}")

    st.subheader("Historial")
    hist = pd.DataFrame(st.session_state.history)
    sel = st.selectbox("Monitor", hist.Monitor.unique())
    h = hist[(hist.Monitor == sel) & hist.Valor.notna()].set_index("Hora")
    if not h.empty:
        st.line_chart(h["Valor"])
    st.dataframe(hist[hist.Estado != OK].tail(50).sort_values("Hora", ascending=False),
                 use_container_width=True)
    st.caption(f"Última comprobación: {datetime.now():%H:%M:%S}")


dashboard()
