# Streamlit Health Monitor

App de monitorización sanitaria tipo SimplMonitor construida con Streamlit.

## Características

- **Pacientes**: ritmo cardiaco (lpm), tensión arterial sistólica/diastólica (mmHg) y saturación de oxígeno (SpO2 %), con semáforo por constante, alertas y gráficas de tendencia
- **Sistemas**: monitores HTTP, puertos TCP y uso de disco
- Auto-refresco configurable e historial de alertas

> Las constantes vitales son **simuladas**. Sustituye `next_reading` en `vitals.py` por una integración real (HL7/FHIR/API del monitor).

## Instalación y ejecución

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Configuración

- `config.json`: lista de monitores de sistemas y de pacientes.
- `vitals.py`: rangos de aviso/fallo de cada constante (`LIMITS`).
