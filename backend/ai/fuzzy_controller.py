import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

class FuzzyAcuaponiaController:
    def __init__(self):
        # ==========================================
        # 1. ENTRADAS (ANTECEDENTES)
        # ==========================================
        self.temp = ctrl.Antecedent(np.arange(0, 45, 0.5), 'temperature')
        self.do = ctrl.Antecedent(np.arange(0, 15, 0.1), 'dissolved_oxygen')
        self.ammonia = ctrl.Antecedent(np.arange(0, 10, 0.05), 'ammonia')
        self.nitrite = ctrl.Antecedent(np.arange(0, 10, 0.05), 'nitrite')
        self.turbidity = ctrl.Antecedent(np.arange(0, 100, 1), 'turbidity')

        # ==========================================
        # 2. SALIDAS (CONSECUENTES)
        # ==========================================
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

        # --- SALIDAS (%) ---
        # Aireación
        self.aeration['baja'] = fuzzy.trimf(self.aeration.universe, [0, 0, 40])
        self.aeration['media'] = fuzzy.trimf(self.aeration.universe, [30, 60, 80])
        self.aeration['alta'] = fuzzy.trimf(self.aeration.universe, [70, 100, 100])

        # Calefacción
        self.heating['apagado'] = fuzzy.trimf(self.heating.universe, [0, 0, 10])
        self.heating['medio'] = fuzzy.trimf(self.heating.universe, [5, 50, 75])
        self.heating['alto'] = fuzzy.trimf(self.heating.universe, [60, 100, 100])

        # Recirculación
        self.recirculation['minima'] = fuzzy.trimf(self.recirculation.universe, [0, 10, 30])
        self.recirculation['normal'] = fuzzy.trimf(self.recirculation.universe, [25, 50, 75])
        self.recirculation['maxima'] = fuzzy.trimf(self.recirculation.universe, [70, 100, 100])

    def _build_rules(self):
        rules = [
            # Reglas de Aireación y Oxígeno
            ctrl.Rule(self.do['critico'], self.aeration['alta']),
            ctrl.Rule(self.do['moderado'], self.aeration['media']),
            ctrl.Rule(self.do['optimo'] & self.ammonia['seguro'], self.aeration['baja']),

            # Reglas de Temperatura y Calefacción
            ctrl.Rule(self.temp['fria'], self.heating['alto']),
            ctrl.Rule(self.temp['optima'], self.heating['apagado']),
            ctrl.Rule(self.temp['caliente'], self.heating['apagado']),

            # Reglas de Recirculación y Calidad Biológica
            ctrl.Rule(self.ammonia['toxico'] | self.nitrite['alto'], self.recirculation['maxima']),
            ctrl.Rule(self.ammonia['alerta'], self.recirculation['normal']),
            ctrl.Rule(self.turbidity['turbia'], self.recirculation['maxima']),
            ctrl.Rule(self.ammonia['seguro'] & self.nitrite['bajo'] & self.turbidity['clara'], self.recirculation['minima']),

            # Reglas de Emergencia Combinada
            ctrl.Rule(self.do['critico'] & self.ammonia['toxico'], (self.aeration['alta'], self.recirculation['maxima'])),
            ctrl.Rule(self.temp['fria'] & self.do['critico'], (self.heating['alto'], self.aeration['alta']))
        ]

        self.control_system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def evaluate(self, temperature: float, dissolved_oxygen: float, ammonia: float, nitrite: float = 0.0, turbidity: float = 10.0):
        """Calcula la respuesta de aireación, calefacción y recirculación en %."""
        self.simulation.input['temperature'] = temperature
        self.simulation.input['dissolved_oxygen'] = dissolved_oxygen
        self.simulation.input['ammonia'] = ammonia
        self.simulation.input['nitrite'] = nitrite
        self.simulation.input['turbidity'] = turbidity

        self.simulation.compute()

        return {
            "aeration_rate": round(float(self.simulation.output.get('aeration_rate', 0)), 2),
            "heating_power": round(float(self.simulation.output.get('heating_power', 0)), 2),
            "recirculation_flow": round(float(self.simulation.output.get('recirculation_flow', 0)), 2),
        }