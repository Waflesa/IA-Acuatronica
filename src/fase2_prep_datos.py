import pandas as pd
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

COLUMNAS_X = [
    "Temp", "Turbidity (cm)", "DO(mg/L)", "BOD (mg/L)", "CO2", "pH",
    "Alkalinity (mg L-1 )", "Hardness (mg L-1 )", "Calcium (mg L-1 )",
    "Ammonia (mg L-1 )", "Nitrite (mg L-1 )", "Phosphorus (mg L-1 )",
    "H2S (mg L-1 )", "Plankton (No. L-1)"
]
COLUMNA_Y = "Water Quality"


def preparar_caracteristicas_y_etiqueta(base_dir: Path = BASE_DIR) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(base_dir / "Data" / "WQD_Limpio.csv")
    X = df[COLUMNAS_X]
    y = df[COLUMNA_Y]
    return X, y


def verificar_preparacion(X: pd.DataFrame, y: pd.Series) -> None:
    print("X:")
    print(X.head())
    print("\ny:")
    print(y.head())
    print("\nDimensiones X:", X.shape)
    print("Dimensiones y:", y.shape)


if __name__ == "__main__":
    X, y = preparar_caracteristicas_y_etiqueta()
    verificar_preparacion(X, y)
