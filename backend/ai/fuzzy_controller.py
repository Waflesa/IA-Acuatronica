import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.fase3_entrenamiento import FuzzyAcuaponiaController

class FuzzyControllerWrapper:
    def __init__(self):
        self.controller = FuzzyAcuaponiaController()

    def evaluate(self, temperature: float, dissolved_oxygen: float, ammonia: float, nitrite: float = 0.0, turbidity: float = 10.0) -> dict:
        return self.controller.evaluate(
            temperature=temperature,
            dissolved_oxygen=dissolved_oxygen,
            ammonia=ammonia,
            nitrite=nitrite,
            turbidity=turbidity
        )