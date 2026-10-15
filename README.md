# Streamlit Health Monitor

App de monitorización sanitaria tipo SimplMonitor construida con Streamlit.

## Características

- Monitores de servicios HTTP
- Monitores de puertos TCP
- Monitor de uso de disco
- Simulación de constantes de paciente (FC/SpO2)
- Dashboard en tiempo real con auto-refresco
- Historial y alertas de servicios críticos

## Requisitos

- Python 3.10+

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Configuración

Edita `config.json` para añadir o cambiar monitores.
