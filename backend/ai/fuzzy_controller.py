import sys
from pathlib import Path
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


class FuzzyAcuaponiaController:
    def __init__(self):
        # 1. ENTRADAS (ANTECEDENTES)
        self.temp = ctrl.Antecedent(np.arange(0, 45, 0.5), 'temperature')
        self.do = ctrl.Antecedent(np.arange(0, 15, 0.1), 'dissolved_oxygen')
        self.ammonia = ctrl.Antecedent(np.arange(0, 10, 0.05), 'ammonia')
        self.nitrite = ctrl.Antecedent(np.arange(0, 10, 0.05), 'nitrite')
        self.turbidity = ctrl.Antecedent(np.arange(0, 100, 1), 'turbidity')

        # 2. SALIDAS (CONSECUENTES)
        self.aeration = ctrl.Consequent(np.arange(0, 101, 1), 'aeration_rate')
        self.heating = ctrl.Consequent(np.arange(0, 101, 1), 'heating_power')
        self.recirculation = ctrl.Consequent(np.arange(0, 101, 1), 'recirculation_flow')

        self._build_membership_functions()
        self._build_rules()

    def _build_membership_functions(self):
        # Temperatura (°C)
        self.temp['fria'] = fuzzy.trimf(self.temp.universe, [0, 0, 20])
        self.temp['optima'] = fuzzy.trimf(self.temp.universe, [18, 24, 28])
        self.temp['caliente'] = fuzzy.trimf(self.temp.universe, [26, 45, 45])

        # Oxígeno Disuelto - DO (mg/L)
        self.do['critico'] = fuzzy.trimf(self.do.universe, [0, 0, 4])
        self.do['moderado'] = fuzzy.trimf(self.do.universe, [3, 5, 7])
        self.do['optimo'] = fuzzy.trimf(self.do.universe, [6, 15, 15])

        # Amonio (mg/L)
        self.ammonia['seguro'] = fuzzy.trimf(self.ammonia.universe, [0, 0, 0.5])
        self.ammonia['alerta'] = fuzzy.trimf(self.ammonia.universe, [0.3, 1.5, 3.0])
        self.ammonia['toxico'] = fuzzy.trimf(self.ammonia.universe, [2.0, 10, 10])

        # Nitritos (mg/L)
        self.nitrite['bajo'] = fuzzy.trimf(self.nitrite.universe, [0, 0, 1.0])
        self.nitrite['alto'] = fuzzy.trimf(self.nitrite.universe, [0.8, 10, 10])

        # Turbidez (cm)
        self.turbidity['clara'] = fuzzy.trimf(self.turbidity.universe, [0, 0, 30])
        self.turbidity['turbia'] = fuzzy.trimf(self.turbidity.universe, [20, 100, 100])

        # SALIDAS (%)
        self.aeration['baja'] = fuzzy.trimf(self.aeration.universe, [0, 0, 40])
        self.aeration['media'] = fuzzy.trimf(self.aeration.universe, [30, 60, 80])
        self.aeration['alta'] = fuzzy.trimf(self.aeration.universe, [70, 100, 100])

        self.heating['apagado'] = fuzzy.trimf(self.heating.universe, [0, 0, 10])
        self.heating['medio'] = fuzzy.trimf(self.heating.universe, [5, 50, 75])
        self.heating['alto'] = fuzzy.trimf(self.heating.universe, [60, 100, 100])

        self.recirculation['baja'] = fuzzy.trimf(self.recirculation.universe, [0, 0, 30])
        self.recirculation['media'] = fuzzy.trimf(self.recirculation.universe, [20, 50, 80])
        self.recirculation['alta'] = fuzzy.trimf(self.recirculation.universe, [70, 100, 100])

    def _build_rules(self):
        r1 = ctrl.Rule(self.do['critico'], self.aeration['alta'])
        r2 = ctrl.Rule(self.do['moderado'], self.aeration['media'])
        r3 = ctrl.Rule(self.do['optimo'], self.aeration['baja'])

        r4 = ctrl.Rule(self.temp['fria'], self.heating['alto'])
        r5 = ctrl.Rule(self.temp['optima'], self.heating['apagado'])
        r6 = ctrl.Rule(self.temp['caliente'], self.heating['apagado'])

        # Se vincula la turbidez con la velocidad de recirculación
        r7 = ctrl.Rule(self.ammonia['toxico'] | self.nitrite['alto'] | self.turbidity['turbia'], self.recirculation['alta'])
        r8 = ctrl.Rule(self.ammonia['alerta'], self.recirculation['media'])
        r9 = ctrl.Rule(self.ammonia['seguro'] & self.nitrite['bajo'] & self.turbidity['clara'], self.recirculation['baja'])

        self.system = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6, r7, r8, r9])
        self.sim = ctrl.ControlSystemSimulation(self.system)

    def evaluate(self, temperature: float, dissolved_oxygen: float, ammonia: float, nitrite: float = 0.0, turbidity: float = 10.0) -> dict:
        self.sim.input['temperature'] = min(max(temperature, 0), 44.5)
        self.sim.input['dissolved_oxygen'] = min(max(dissolved_oxygen, 0), 14.9)
        self.sim.input['ammonia'] = min(max(ammonia, 0), 9.9)
        self.sim.input['nitrite'] = min(max(nitrite, 0), 9.9)
        self.sim.input['turbidity'] = min(max(turbidity, 0), 99)

        self.sim.compute()

        return {
            "aeration_rate": round(self.sim.output.get('aeration_rate', 50.0), 1),
            "heating_power": round(self.sim.output.get('heating_power', 0.0), 1),
            "recirculation_flow": round(self.sim.output.get('recirculation_flow', 30.0), 1)
        }


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