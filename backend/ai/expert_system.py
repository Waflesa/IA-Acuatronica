"""Sistema experto híbrido: clasificador ML (calidad de agua) + motor de reglas.

Adaptado del módulo del compañero (Acuatronica_MotorIA):
- fase3_entrenamiento.py  -> modelo RandomForest (modelo_calidad_agua.joblib)
- fase4_sistema_experto.py -> MotorInferenciaAcuatronica + base de conocimiento

Contrato de salida (compatible con backend/main.py, no requiere cambios en el
WebSocket):  diagnose(sample) -> {"status", "alerts", "protocols",
"water_quality", "water_quality_class"}
"""

import os
import warnings

import joblib
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "modelo_calidad_agua.joblib",
)

# Umbrales del motor (mismos que fase4_sistema_experto.py del compañero)
UMBRAL_AMONIO = 0.5
UMBRAL_NITRITO = 2.5
UMBRAL_DO_BAJO = 3.0

ETIQUETAS_CALIDAD = {0: "Buena", 1: "Moderada", 2: "Mala / Critica"}

# Nombre interno (dataset limpio, ver data_engine.dataset_loader) -> nombre
# original que espera el modelo ML (debe respetar el orden de feature_names_in_)
MAPEO_COLUMNAS = {
    "temperature": "Temp",
    "turbidity": "Turbidity (cm)",
    "dissolved_oxygen": "DO(mg/L)",
    "bod": "BOD (mg/L)",
    "co2": "CO2",
    "ph": "pH",
    "alkalinity": "Alkalinity (mg L-1 )",
    "hardness": "Hardness (mg L-1 )",
    "calcium": "Calcium (mg L-1 )",
    "ammonia": "Ammonia (mg L-1 )",
    "nitrite": "Nitrite (mg L-1 )",
    "phosphorus": "Phosphorus (mg L-1 )",
    "h2s": "H2S (mg L-1 )",
    "plankton": "Plankton (No. L-1)",
}

# Valores típicos para variables que el modo "manual" no envía
VALORES_POR_DEFECTO = {
    "bod": 5.0,
    "co2": 8.0,
    "ph": 7.0,
    "alkalinity": 90.0,
    "hardness": 110.0,
    "calcium": 60.0,
    "phosphorus": 1.0,
    "h2s": 0.02,
    "plankton": 3500.0,
}


class MotorInferenciaAcuatronica:
    """Motor de reglas de diagnóstico (copia silenciosa de fase4)."""

    def __init__(self):
        self.hechos = {}
        self.reglas = []

    def agregar_hecho(self, variable, valor):
        self.hechos[variable] = valor

    def agregar_regla(self, condiciones, conclusion, valor_conclusion):
        self.reglas.append({
            "condiciones": condiciones,
            "conclusion": conclusion,
            "valor_conclusion": valor_conclusion,
        })

    def ejecutar(self):
        cambios = True
        while cambios:
            cambios = False
            for regla in self.reglas:
                conclusion = regla["conclusion"]
                if conclusion in self.hechos:
                    continue
                se_cumplen = True
                for variable, valor_esperado in regla["condiciones"].items():
                    valor_actual = self.hechos.get(variable)
                    if type(valor_esperado) is str and valor_esperado.startswith(">"):
                        limite = float(valor_esperado[1:])
                        if valor_actual is None or valor_actual <= limite:
                            se_cumplen = False
                            break
                    elif type(valor_esperado) is str and valor_esperado.startswith("<"):
                        limite = float(valor_esperado[1:])
                        if valor_actual is None or valor_actual >= limite:
                            se_cumplen = False
                            break
                    elif valor_actual != valor_esperado:
                        se_cumplen = False
                        break
                if se_cumplen:
                    self.agregar_hecho(conclusion, regla["valor_conclusion"])
                    cambios = True
        return self.hechos


def construir_base_conocimiento(motor):
    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": True, "alerta_toxicidad_nitrito": True},
        conclusion="protocolo_mitigacion",
        valor_conclusion="EMERGENCIA: cambio parcial de agua urgente + revision del biofiltro",
    )
    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": True, "alerta_toxicidad_nitrito": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Reducir alimentacion + aumentar recirculacion para diluir amonio",
    )
    motor.agregar_regla(
        condiciones={"alerta_toxicidad_nitrito": True, "alerta_toxicidad_amonio": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Anadir sal aclimatada + monitorear ciclo de nitrificacion",
    )
    motor.agregar_regla(
        condiciones={"posible_falla_aireacion": True, "alerta_toxicidad_amonio": False,
                     "alerta_toxicidad_nitrito": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Falla mecanica probable: activar aireador de respaldo + revisar bomba/filtro",
    )
    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": False, "alerta_toxicidad_nitrito": False,
                     "posible_falla_aireacion": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Parametros dentro de rango: monitoreo estandar",
    )


class WaterExpertSystem:
    """Clasifica la calidad del agua (ML) y diagnostica con el motor de reglas."""

    def __init__(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.modelo = joblib.load(MODEL_PATH)
        self._columnas_modelo = list(self.modelo.feature_names_in_)

    def _fila_modelo(self, sensor_data):
        fila = {}
        for limpio, original in MAPEO_COLUMNAS.items():
            valor = sensor_data.get(limpio)
            if valor is None:
                valor = VALORES_POR_DEFECTO.get(limpio, 0.0)
            fila[original] = valor
        return pd.DataFrame([fila])[self._columnas_modelo]

    def _clasificar(self, sensor_data):
        clase = int(self.modelo.predict(self._fila_modelo(sensor_data))[0])
        return clase

    def diagnose(self, sensor_data):
        am = sensor_data.get("ammonia", 0.0)
        nt = sensor_data.get("nitrite", 0.0)
        do = sensor_data.get("dissolved_oxygen", 6.0)

        motor = MotorInferenciaAcuatronica()
        construir_base_conocimiento(motor)
        motor.agregar_hecho("alerta_toxicidad_amonio", am > UMBRAL_AMONIO)
        motor.agregar_hecho("alerta_toxicidad_nitrito", nt > UMBRAL_NITRITO)
        motor.agregar_hecho("posible_falla_aireacion", do < UMBRAL_DO_BAJO)
        clase = self._clasificar(sensor_data)
        motor.agregar_hecho("clase_calidad_ml", clase)
        hechos = motor.ejecutar()

        protocolo = hechos.get("protocolo_mitigacion", "Parametros dentro de rango: monitoreo estandar")

        alerts = []
        protocols = [protocolo]
        if hechos.get("alerta_toxicidad_amonio"):
            alerts.append("Toxicidad por amonio (NH3) elevado")
        if hechos.get("alerta_toxicidad_nitrito"):
            alerts.append("Toxicidad por nitritos (NO2) elevado")
        if hechos.get("posible_falla_aireacion"):
            alerts.append("Oxigeno disuelto bajo: posible falla de aireacion")
        if clase == 2:
            alerts.append("Calidad del agua critica (ML)")
        elif clase == 1:
            alerts.append("Calidad del agua moderada (ML)")

        if clase == 2 or (hechos.get("alerta_toxicidad_amonio") and hechos.get("alerta_toxicidad_nitrito")):
            status = "CRITICAL"
        elif alerts:
            status = "WARNING"
        else:
            status = "OPTIMAL"

        return {
            "status": status,
            "alerts": alerts,
            "protocols": protocols,
            "water_quality": ETIQUETAS_CALIDAD.get(clase, str(clase)),
            "water_quality_class": clase,
        }


if __name__ == "__main__":
    # Prueba: escenario de agua fría, oxígeno bajo y amonio elevado
    muestra = {
        "temperature": 15.0,
        "dissolved_oxygen": 2.1,
        "ammonia": 2.5,
        "nitrite": 1.2,
        "turbidity": 40.0,
    }
    print(WaterExpertSystem().diagnose(muestra))