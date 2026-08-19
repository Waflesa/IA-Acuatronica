import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import pathlib 
try:
    from src.fase2_prep_datos import preparar_caracteristicas_y_etiqueta
except ModuleNotFoundError:
    from fase2_prep_datos import preparar_caracteristicas_y_etiqueta


def entrenar_evaluar_guardar(
    base_dir: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent,
    ruta_dataset: str = "Data/WQD_Limpio.csv",
    ruta_modelo: str = "Models/modelo_calidad_agua.joblib",
    ruta_reporte: str = "Reports/metrics_fase3.txt"
) -> tuple[RandomForestClassifier, float]:
    X, y = preparar_caracteristicas_y_etiqueta(base_dir)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    reporte = classification_report(y_test, y_pred, zero_division=0)

    contenido_reporte = (
        "METRICAS FASE 3 - MODELO ML (CALIDAD DE AGUA)\n"
        f"Accuracy: {acc * 100:.2f}%\n\n"
        "Matriz de Confusion:\n"
        f"{cm}\n\n"
        "Reporte de Clasificacion:\n"
        f"{reporte}\n"
    )

    print(contenido_reporte)

    os.makedirs(os.path.dirname(ruta_reporte), exist_ok=True)
    os.makedirs(os.path.dirname(ruta_modelo), exist_ok=True)

    with open(ruta_reporte, "w", encoding="utf-8") as f:
        f.write(contenido_reporte)
    print(f"Reporte guardado: {ruta_reporte}")

    joblib.dump(modelo, ruta_modelo)
    print(f"Modelo guardado: {ruta_modelo}")

    return modelo, acc


if __name__ == "__main__":
    entrenar_evaluar_guardar()
