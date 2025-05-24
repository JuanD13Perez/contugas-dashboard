# api.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import pickle
import io
from datetime import datetime, timedelta
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any

# Inicializar FastAPI
app = FastAPI(title="Contugas Prediction API")

# Configurar CORS para permitir solicitudes desde el dashboard
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],  # En producción, limitar a la URL del dashboard
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# Cargar modelos pre-entrenados
try:
    with open('models/lstm_models.pkl', 'rb') as f:
        modelos = pickle.load(f)
    print(f"Modelos cargados exitosamente para {len(modelos)} clientes")
except Exception as e:
    print(f"Error al cargar modelos: {e}")
    modelos = {}

# Cargar datos históricos
try:
    df_historico = pd.read_csv("data/predicted_with_anomalies_and_future.csv", parse_dates=["Fecha"])
    print(f"Datos históricos cargados: {len(df_historico)} registros")
except Exception as e:
    print(f"Error al cargar datos históricos: {str(e)}")
    df_historico = pd.DataFrame()

# Definir modelos de datos
class PredictionRequest(BaseModel):
    client_id: str
    data: List[Dict[str, Any]]

class PredictionResponse(BaseModel):
    status: str
    message: str
    predictions: List[Dict[str, Any]] = None
    future_predictions: List[Dict[str, Any]] = None

@app.get("/")
def read_root():
    return {"message": "Contugas Prediction API", "status": "active"}

@app.get("/clients")
def get_clients():
    """Obtener lista de clientes disponibles"""
    return {"clients": list(modelos.keys())}

@app.get("/historical-data/{client_id}")
def get_historical_data(client_id: str, days: int = 30):
    """Obtener datos históricos y estadísticas de anomalías para un cliente"""
    if df_historico.empty:
        raise HTTPException(status_code=500, detail="No se han cargado los datos históricos")
    
    # Filtrar datos para el cliente
    df_cliente = df_historico[df_historico["Client_ID"] == client_id]
    
    if df_cliente.empty:
        raise HTTPException(status_code=404, detail=f"No hay datos históricos para el cliente {client_id}")
    
    # Obtener datos del último mes (o los días especificados)
    fecha_max = df_cliente["Fecha"].max()
    fecha_inicio = fecha_max - pd.Timedelta(days=days)
    df_reciente = df_cliente[df_cliente["Fecha"] >= fecha_inicio]
    
    # Calcular estadísticas de anomalías
    df_anomalias = df_reciente[df_reciente["Anomaly"] == -1]
    num_anomalias = len(df_anomalias)
    
    # Calcular promedios de variables para anomalías
    promedios = {}
    if num_anomalias > 0:
        for var in ["Presion_actual", "Temperatura_actual", "Volumen_actual"]:
            promedios[var.replace("_actual", "")] = float(df_anomalias[var].mean())
    
    # Preparar datos históricos para enviar
    datos_historicos = []
    for _, row in df_reciente.iterrows():
        datos_historicos.append({
            "Fecha": row["Fecha"].isoformat(),
            "Presion": float(row["Presion_actual"]),
            "Temperatura": float(row["Temperatura_actual"]),
            "Volumen": float(row["Volumen_actual"]),
            "Anomaly": int(row["Anomaly"])
        })
    
    return {
        "historical_data": datos_historicos,
        "anomaly_count": num_anomalias,
        "anomaly_averages": promedios
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Realizar predicciones para un cliente específico"""
    client_id = request.client_id
    data = request.data
    
    # Verificar si existe modelo para este cliente
    if client_id not in modelos:
        raise HTTPException(status_code=404, detail=f"No hay modelo disponible para el cliente {client_id}")
    
    # Convertir datos a DataFrame
    try:
        df = pd.DataFrame(data)
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df = df.sort_values("Fecha")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar los datos: {str(e)}")
    
    # Realizar predicciones
    try:
        y_pred_inv, fechas_pred, y_futuro_inv, fechas_futuro = procesar_nuevos_datos(df, client_id)
        
        # Formatear resultados
        predictions = []
        if len(fechas_pred) > 0:
            for i in range(len(fechas_pred)):
                predictions.append({
                    "Fecha": fechas_pred[i].isoformat(),
                    "Presion": float(y_pred_inv[i, 0]),
                    "Temperatura": float(y_pred_inv[i, 1]),
                    "Volumen": float(y_pred_inv[i, 2])
                })
        
        future_predictions = []
        for i in range(len(fechas_futuro)):
            future_predictions.append({
                "Fecha": fechas_futuro[i].isoformat(),
                "Presion": float(y_futuro_inv[i, 0]),
                "Temperatura": float(y_futuro_inv[i, 1]),
                "Volumen": float(y_futuro_inv[i, 2])
            })
        
        return {
            "status": "success",
            "message": "Predicciones generadas correctamente",
            "predictions": predictions,
            "future_predictions": future_predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar predicciones: {str(e)}")

@app.post("/upload-predict/{client_id}")
async def upload_predict(client_id: str, file: UploadFile = File(...)):
    """Cargar archivo Excel y realizar predicciones"""
    if client_id not in modelos:
        raise HTTPException(status_code=404, detail=f"No hay modelo disponible para el cliente {client_id}")
    
    # Leer archivo Excel
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Verificar columnas requeridas
        required_cols = ["Fecha", "Presion", "Temperatura", "Volumen"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Faltan columnas requeridas: {', '.join(missing_cols)}")
        
        # Convertir Fecha a datetime
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        
        # Realizar predicciones
        y_pred_inv, fechas_pred, y_futuro_inv, fechas_futuro = procesar_nuevos_datos(df, client_id)
        
        # Formatear resultados
        predictions = []
        if len(fechas_pred) > 0:
            for i in range(len(fechas_pred)):
                predictions.append({
                    "Fecha": fechas_pred[i].isoformat(),
                    "Presion": float(y_pred_inv[i, 0]),
                    "Temperatura": float(y_pred_inv[i, 1]),
                    "Volumen": float(y_futuro_inv[i, 2])
                })
        
        future_predictions = []
        for i in range(len(fechas_futuro)):
            future_predictions.append({
                "Fecha": fechas_futuro[i].isoformat(),
                "Presion": float(y_futuro_inv[i, 0]),
                "Temperatura": float(y_futuro_inv[i, 1]),
                "Volumen": float(y_futuro_inv[i, 2])
            })
        
        return {
            "status": "success",
            "message": "Archivo procesado correctamente",
            "predictions": predictions,
            "future_predictions": future_predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

def procesar_nuevos_datos(df, cliente_id, ventana=24, pasos_futuros=24):
    """Procesa nuevos datos y genera predicciones"""
    # Obtener modelo y scaler para el cliente
    model, scaler = modelos[cliente_id]
    
    # Verificar que hay suficientes datos
    if len(df) < ventana:
        raise ValueError(f"Se necesitan al menos {ventana} registros para hacer predicciones")
    
    # Escalar los datos
    variables = df[["Presion", "Temperatura", "Volumen"]].values
    variables_escaladas = scaler.transform(variables)
    
    # Predicción sobre los datos existentes
    y_pred = []
    fechas_pred = []
    
    for i in range(len(variables_escaladas) - ventana):
        ventana_input = variables_escaladas[i:i+ventana]
        pred = model.predict(ventana_input.reshape(1, ventana, -1), verbose=0)
        y_pred.append(pred[0])
        fechas_pred.append(df["Fecha"].iloc[i + ventana])
    
    y_pred_inv = scaler.inverse_transform(np.array(y_pred)) if y_pred else np.empty((0, 3))
    
    # Predicción futura (24 horas siguientes)
    secuencia = variables_escaladas[-ventana:].copy()
    y_futuro = []
    
    for _ in range(pasos_futuros):
        entrada = secuencia[-ventana:].reshape(1, ventana, -1)
        pred = model.predict(entrada, verbose=0)
        y_futuro.append(pred[0])
        secuencia = np.vstack([secuencia, pred])
    
    y_futuro_inv = scaler.inverse_transform(np.array(y_futuro))
    ultima_fecha = df["Fecha"].iloc[-1]
    fechas_futuro = pd.date_range(start=ultima_fecha + timedelta(hours=1), periods=pasos_futuros, freq='H')
    
    return y_pred_inv, fechas_pred, y_futuro_inv, fechas_futuro

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=port)