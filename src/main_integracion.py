import pandas as pd
import joblib

try:
    from src.fase2_prep_datos import COLUMNAS_X
    from src.fase4_sistema_experto import (
        MotorInferenciaAcuatronica,
        construir_base_conocimiento,
        evaluar_toxicidad_amonio,
        evaluar_toxicidad_nitrito,
        evaluar_falla_aireacion,
    )
except ModuleNotFoundError:
    from fase2_prep_datos import COLUMNAS_X
    from fase4_sistema_experto import (
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


def main():
    modelo_ml = joblib.load("models/modelo_calidad_agua.joblib")

    # lectura de sensores de ejemplo (en un caso real vendria del hardware)
    lectura_sensores = {
        "Temp": 29.5,
        "Turbidity (cm)": 45.0,
        "DO(mg/L)": 2.1,
        "BOD (mg/L)": 5.2,
        "CO2": 8.3,
        "pH": 6.8,
        "Alkalinity (mg L-1 )": 90.0,
        "Hardness (mg L-1 )": 110.0,
        "Calcium (mg L-1 )": 60.0,
        "Ammonia (mg L-1 )": 0.62,
        "Nitrite (mg L-1 )": 0.8,
        "Phosphorus (mg L-1 )": 1.0,
        "H2S (mg L-1 )": 0.02,
        "Plankton (No. L-1)": 3500.0,
    }

    df_muestra = pd.DataFrame([lectura_sensores])[COLUMNAS_X]

    clase_predicha = int(modelo_ml.predict(df_muestra)[0])
    probabilidades = modelo_ml.predict_proba(df_muestra)[0]

    print(f"Clase predicha: {clase_predicha} ({ETIQUETAS_CALIDAD[clase_predicha]})")
    print(f"Probabilidades: {dict(zip(modelo_ml.classes_, probabilidades.round(3)))}\n")

    motor = MotorInferenciaAcuatronica()
    construir_base_conocimiento(motor)

    motor.agregar_hecho(
        "alerta_toxicidad_amonio",
        evaluar_toxicidad_amonio(lectura_sensores["Ammonia (mg L-1 )"])
    )
    motor.agregar_hecho(
        "alerta_toxicidad_nitrito",
        evaluar_toxicidad_nitrito(lectura_sensores["Nitrite (mg L-1 )"])
    )
    motor.agregar_hecho(
        "posible_falla_aireacion",
        evaluar_falla_aireacion(lectura_sensores["DO(mg/L)"])
    )
    motor.agregar_hecho("clase_calidad_ml", clase_predicha)

    resultado = motor.ejecutar()

    print("\n--- REPORTE FINAL ---")
    print(f"Calidad del agua (ML): {clase_predicha} ({ETIQUETAS_CALIDAD[clase_predicha]})")
    print(f"Protocolo a aplicar: {resultado.get('protocolo_mitigacion', 'Sin diagnostico')}")


if __name__ == "__main__":
    main()
