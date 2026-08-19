from pathlib import Path
import pandas as pd
import os


BASE_DIR = Path(__file__).resolve().parent.parent

RUTA_ENTRADA = BASE_DIR / "Data" / "WQD.csv"
RUTA_SALIDA = BASE_DIR / "Data" / "WQD_Limpio.csv"
RUTA_REPORTE = BASE_DIR / "reports" / "metrics_fase1.txt"


def cargar_y_verificar() -> pd.DataFrame:
    df = pd.read_csv(RUTA_ENTRADA)

    total_nulos = int(df.isnull().sum().sum())
    total_duplicados = int(df.duplicated().sum())
    dimensiones = df.shape

    negativos = {}

    for col in df.select_dtypes(include="number").columns:
        n_neg = int((df[col] < 0).sum())

        if n_neg > 0:
            negativos[col] = n_neg

    contenido_reporte = (
        "REPORTE DE VERIFICACION - FASE 1 (WQD)\n"
        f"Dimensiones: {dimensiones[0]} filas x {dimensiones[1]} columnas\n"
        f"Valores nulos: {total_nulos}\n"
        f"Filas duplicadas: {total_duplicados}\n"
        f"Columnas con negativos: "
        f"{negativos if negativos else 'Ninguna'}\n\n"
        "No se realizo limpieza porque el dataset ya venia completo, "
        "sin nulos ni duplicados, asi que no hubo nada que rellenar "
        "ni eliminar.\n"
    )

    print(contenido_reporte)

    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(RUTA_SALIDA, index=False)

    with open(RUTA_REPORTE, "w", encoding="utf-8") as f:
        f.write(contenido_reporte)

    print(f"Guardado: {RUTA_SALIDA}")
    print(f"Reporte: {RUTA_REPORTE}")

    return df


if __name__ == "__main__":
    cargar_y_verificar()