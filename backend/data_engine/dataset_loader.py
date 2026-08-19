import pandas as pd
import numpy as np

class DatasetEngine:
    def __init__(self, filepath: str):
        self.df = pd.read_excel(filepath)
        self.current_index = 0
        self.total_rows = len(self.df)

    def get_next_sample(self) -> dict:
        if self.df.empty:
            return {}

        # Obtener la fila actual
        row = self.df.iloc[self.current_index].to_dict()

        # Incrementar el índice cíclicamente
        self.current_index = (self.current_index + 1) % self.total_rows

        # Mapeo y pequeña variación aleatoria para dinamismo en tiempo real
        sample = {
            "temperature": round(float(row.get("temperature", 25.0)) + np.random.uniform(-0.1, 0.1), 2),
            "dissolved_oxygen": round(float(row.get("dissolved_oxygen", 6.5)) + np.random.uniform(-0.08, 0.08), 2),
            "ammonia": round(float(row.get("ammonia", 0.25)) + np.random.uniform(-0.02, 0.02), 2),
            "nitrite": round(float(row.get("nitrite", 0.20)) + np.random.uniform(-0.02, 0.02), 2),
            "ph": round(float(row.get("ph", 7.0)) + np.random.uniform(-0.03, 0.03), 2),
            "recirculation_flow": round(float(row.get("recirculation_flow", 11.5)) + np.random.uniform(-0.1, 0.1), 2),
            "turbidity": round(float(row.get("turbidity", 10.0)), 2)
        }

        return sample