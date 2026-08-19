import sys
from pathlib import Path
import joblib
import pandas as pd

# Asegurar que la raíz del proyecto esté en el PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.fase2_prep_datos import COLUMNAS_X
from src.fase4_sistema_experto import (
    MotorInferenciaAcuatronica,
    construir_base_conocimiento,
    evaluar_toxicidad_amonio,
    evaluar_toxicidad_nitrito,
    evaluar_falla_aireacion,
)

ETIQUETAS_CALIDAD = {
    0: "Buena",
    1: "Moderada",
    2: "Mala / Critica",
}

class WaterExpertSystem:
    def __init__(self):
        # Cargar el modelo entrenado en la Fase 3
        model_path = BASE_DIR / "models" / "modelo_calidad_agua.joblib"
        if model_path.exists():
            self.model = joblib.load(model_path)
        else:
            self.model = None
            print(f"[WARN] No se encontró el modelo en {model_path}")

    def diagnose(self, sensor_data: dict) -> dict:
        """
        sensor_data viene del WebSocket o simulador con claves estándar.
        Ejemplo: {"temperature": 29.5, "dissolved_oxygen": 2.1, "ammonia": 0.62, ...}
        """
        # 1. Mapear diccionario de entrada al formato de las 14 columnas del modelo de ML
        row_14_params = {
            "Temp": sensor_data.get("temperature", sensor_data.get("Temp", 25.0)),
            "Turbidity (cm)": sensor_data.get("turbidity", sensor_data.get("Turbidity (cm)", 40.0)),
            "DO(mg/L)": sensor_data.get("dissolved_oxygen", sensor_data.get("DO(mg/L)", 6.0)),
            "BOD (mg/L)": sensor_data.get("bod", sensor_data.get("BOD (mg/L)", 5.0)),
            "CO2": sensor_data.get("co2", sensor_data.get("CO2", 8.0)),
            "pH": sensor_data.get("ph", sensor_data.get("pH", 7.0)),
            "Alkalinity (mg L-1 )": sensor_data.get("alkalinity", sensor_data.get("Alkalinity (mg L-1 )", 90.0)),
            "Hardness (mg L-1 )": sensor_data.get("hardness", sensor_data.get("Hardness (mg L-1 )", 110.0)),
            "Calcium (mg L-1 )": sensor_data.get("calcium", sensor_data.get("Calcium (mg L-1 )", 60.0)),
            "Ammonia (mg L-1 )": sensor_data.get("ammonia", sensor_data.get("Ammonia (mg L-1 )", 0.1)),
            "Nitrite (mg L-1 )": sensor_data.get("nitrite", sensor_data.get("Nitrite (mg L-1 )", 0.1)),
            "Phosphorus (mg L-1 )": sensor_data.get("phosphorus", sensor_data.get("Phosphorus (mg L-1 )", 1.0)),
            "H2S (mg L-1 )": sensor_data.get("h2s", sensor_data.get("H2S (mg L-1 )", 0.01)),
            "Plankton (No. L-1)": sensor_data.get("plankton", sensor_data.get("Plankton (No. L-1)", 3000.0)),
        }

        # 2. Predicción de Calidad de Agua con ML (Fase 2 / Fase 3)
        calidad_str = "Desconocida"
        if self.model:
            df_muestra = pd.DataFrame([row_14_params])[COLUMNAS_X]
            clase_predicha = int(self.model.predict(df_muestra)[0])
            calidad_str = ETIQUETAS_CALIDAD.get(clase_predicha, "Buena")

        # 3. Inferencia por Motor de Reglas (Fase 4)
        motor = MotorInferenciaAcuatronica()
        construir_base_conocimiento(motor)

        amonio_val = row_14_params["Ammonia (mg L-1 )"]
        nitrito_val = row_14_params["Nitrite (mg L-1 )"]
        do_val = row_14_params["DO(mg/L)"]

        motor.agregar_hecho("alerta_toxicidad_amonio", evaluar_toxicidad_amonio(amonio_val))
        motor.agregar_hecho("alerta_toxicidad_nitrito", evaluar_toxicidad_nitrito(nitrito_val))
        motor.agregar_hecho("posible_falla_aireacion", evaluar_falla_aireacion(do_val))

        hechos_finales = motor.ejecutar()

        # Build Alertas y Protocolos para el frontend
        alerts = []
        protocols = []
        protocolo_text = hechos_finales.get("protocolo_mitigacion")

        if hechos_finales.get("alerta_toxicidad_amonio"):
            alerts.append(f"Toxicidad por Amonio ({amonio_val:.2f} mg/L)")
        if hechos_finales.get("alerta_toxicidad_nitrito"):
            alerts.append(f"Toxicidad por Nitritos ({nitrito_val:.2f} mg/L)")
        if hechos_finales.get("posible_falla_aireacion"):
            alerts.append(f"Falla de aireación: Oxígeno bajo ({do_val:.2f} mg/L)")

        if protocolo_text:
            protocols.append(protocolo_text)

        status = "OPTIMAL"
        if len(alerts) >= 2 or "EMERGENCIA" in str(protocolo_text):
            status = "CRITICAL"
        elif len(alerts) == 1:
            status = "WARNING"

        return {
            "water_quality": calidad_str,
            "status": status,
            "alerts": alerts,
            "protocols": protocols
        }