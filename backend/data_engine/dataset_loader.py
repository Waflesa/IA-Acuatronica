"""Motor de datos: recorre el dataset real de calidad de agua (WQD).

Cada llamada a get_next_sample() devuelve la siguiente fila del dataset en
formato cíclico. El diccionario conserva las columnas originales del CSV
(los 14 parámetros que usa el modelo de ML) y además incluye alias estándar
(temperature, dissolved_oxygen, ammonia, nitrite, ph, turbidity) que usan el
controlador difuso y el frontend.
"""

import math

import pandas as pd


class DatasetEngine:
    def __init__(self, filepath: str):
        self.df = pd.read_csv(filepath)
        self.current_index = 0
        self.total_rows = len(self.df)

    @staticmethod
    def _f(value, default):
        try:
            v = float(value)
            if math.isnan(v):
                return default
            return v
        except (TypeError, ValueError):
            return default

    def get_next_sample(self) -> dict:
        if self.df.empty:
            return {}

        row = self.df.iloc[self.current_index]
        self.current_index = (self.current_index + 1) % self.total_rows

        sample = {
            "temperature": self._f(row.get("Temp"), 25.0),
            "turbidity": self._f(row.get("Turbidity (cm)"), 10.0),
            "dissolved_oxygen": self._f(row.get("DO(mg/L)"), 6.0),
            "ammonia": self._f(row.get("Ammonia (mg L-1 )"), 0.1),
            "nitrite": self._f(row.get("Nitrite (mg L-1 )"), 0.1),
            "ph": self._f(row.get("pH"), 7.0),
            "bod": self._f(row.get("BOD (mg/L)"), 5.0),
            "co2": self._f(row.get("CO2"), 8.0),
            "alkalinity": self._f(row.get("Alkalinity (mg L-1 )"), 90.0),
            "hardness": self._f(row.get("Hardness (mg L-1 )"), 110.0),
            "calcium": self._f(row.get("Calcium (mg L-1 )"), 60.0),
            "phosphorus": self._f(row.get("Phosphorus (mg L-1 )"), 1.0),
            "h2s": self._f(row.get("H2S (mg L-1 )"), 0.01),
            "plankton": self._f(row.get("Plankton (No. L-1)"), 3000.0),
            "water_quality": self._f(row.get("Water Quality"), 0.0),
        }
        return sample