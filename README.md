# Dashboard de Mediciones de Gas – Contugas

## Acceso rápido

- **Dashboard:** [https://contugas-dashboard-production.up.railway.app/](https://contugas-dashboard-production.up.railway.app/)
- **API (Swagger):** [https://contugas-dashboard-production-6acf.up.railway.app/docs](https://contugas-dashboard-production-6acf.up.railway.app/docs)

---

## Descripción general

Este proyecto es una solución integral para el análisis, modelamiento y visualización de datos de medición de gas de clientes de Contugas. Incluye un dashboard interactivo (Dash) y una API de predicción (FastAPI), junto con modelos LSTM preentrenados.

En la raíz encontrarás dos archivos PDF:

- **Manual_de_usuario.pdf:** Guía paso a paso para usuarios finales.
- **Presentacion_Empresarial.pdf:** Presentación ejecutiva del proyecto.

---

## Estructura del repositorio

```
├── app.py # Dashboard principal (Dash)
├── api.py # API de predicción (FastAPI)
├── layout1.py
├── layout2.py
├── layout3.py
├── requirements.txt # Dependencias del proyecto
├── lstm_models.pkl # Modelos preentrenados
├── data/
│ ├── Datos_Contugas_Compacted.csv
│ ├── predicted_with_anomalies_and_future.csv
│ ├── Errores.csv
│ └── Resultados_Modelos.csv
├── assets/
│ ├── ContugasBanner.png
│ ├── uniandes.png
│ ├── MIAD.png
│ ├── ss1.png # Screenshot Análisis Histórico
│ ├── ss2.png # Screenshot Detección de Anomalías
│ └── ss3.png # Screenshot Modelamiento
├── Manual_de_usuario.pdf
└── Presentacion_Empresarial.pdf
```
