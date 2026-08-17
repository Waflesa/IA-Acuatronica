from typing import Dict, Any, List

class WaterExpertSystem:
    def __init__(self):
        # Aquí tu compañero definirá o cargará el motor de reglas
        pass

    def diagnose(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evalúa el vector completo de variables fisicoquímicas y genera
        un diagnóstico, nivel de riesgo y protocolo de remediación.
        """
        alerts: List[str] = []
        protocols: List[str] = []
        status = "OPTIMAL"

        # Extracción de parámetros clave
        ammonia = sensor_data.get("ammonia", 0.0)
        nitrite = sensor_data.get("nitrite", 0.0)
        do = sensor_data.get("dissolved_oxygen", 6.0)
        ph = sensor_data.get("ph", 7.0)

        # Reglas base preliminares (Mock / Plantilla)
        if ammonia > 2.0 or nitrite > 1.5:
            status = "CRITICAL"
            alerts.append("Alta acumulación de toxicidad por Amonio/Nitritos")
            protocols.append("Activar recirculación máxima y reducir ración de alimento en un 50%")

        if do < 3.0:
            status = "WARNING" if status != "CRITICAL" else "CRITICAL"
            alerts.append("Nivel de Oxígeno Disuelto en rango crítico")
            protocols.append("Incrementar aireación al 100% y verificar soplador secundario")

        if ph < 6.0 or ph > 8.5:
            alerts.append("Desviación peligrosa de pH")
            protocols.append("Dosificar regulador de pH según tabla técnica")

        return {
            "status": status,
            "alerts": alerts,
            "protocols": protocols
        }