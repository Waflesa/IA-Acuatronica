import pandas as pd
from typing import Dict, Any


class DatasetEngine:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.current_index = 0
        self._load_and_clean_data()

    def _load_and_clean_data(self):
        """Carga el Excel/CSV y estandariza los nombres de las columnas."""

        # Si guardas el Excel como .xlsx usa read_excel,
        # si lo exportas a .csv usa read_csv
        if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
            self.df = pd.read_excel(self.file_path)
        else:
            self.df = pd.read_csv(self.file_path)

        # Mapeo de columnas a nombres limpios
        rename_map = {
            'Temp': 'temperature',
            'Turbidity (cm)': 'turbidity',
            'DO(mg/L)': 'dissolved_oxygen',
            'BOD (mg/L)': 'bod',
            'CO2': 'co2',
            'pH`': 'ph',
            'Alkalinity (mg L-1 )': 'alkalinity',
            'Hardness (mg L-1 )': 'hardness',
            'Calcium (mg L-1 )': 'calcium',
            'Ammonia (mg L-1 )': 'ammonia',
            'Nitrite (mg L-1 )': 'nitrite',
            'Phosphorus (mg L-1 )': 'phosphorus',
            'H2S (mg L-1 )': 'h2s',
            'Plankton (No. L-1)': 'plankton',
            'Water Quality': 'water_quality_class'
        }

        self.df = self.df.rename(columns=rename_map)

    def get_next_sample(self) -> Dict[str, Any]:
        """Obtiene la fila actual y avanza al siguiente registro."""

        if self.df is None or self.df.empty:
            raise ValueError("El dataset no ha sido cargado.")

        sample = self.df.iloc[self.current_index].to_dict()

        # Avanza en ciclo continuo
        self.current_index = (
            self.current_index + 1
        ) % len(self.df)

        return sample