"""Sistema experto híbrido (reglas simbólicas).

Contrato de salida listo para conectar backend/ai/expert_system.py sin tocar la UI:
diagnosis(values) -> {"nivel_general": str, "hallazgos": [hallazgo]}
hallazgo -> {severity, title, message, protocol}
"""


def diagnosis(values):
    am = values.get("amonio", 0.0)
    nt = values.get("nitrito", 0.0)
    od = values.get("od", 0.0)
    temp = values.get("temp", 0.0)
    ph = values.get("ph", 0.0)
    flujo = values.get("flujo", 0.0)

    hallazgos = []

    if am >= 1.0:
        hallazgos.append(dict(
            severity="crit", title="Toxicidad por amonio (NH₃)",
            message=f"Amonio en {am:.2f} mg/L supera el umbral de toxicidad para la biomasa.",
            protocol=["Reducir alimentación de peces al 50%",
                      "Aumentar recirculación al 90%",
                      "Verificar colonia del biofiltro nitrificante",
                      "Monitorear cada 15 minutos"]))
    elif am >= 0.5:
        hallazgos.append(dict(
            severity="warn", title="Amonio elevado",
            message=f"Amonio en {am:.2f} mg/L, próximo al umbral de toxicidad.",
            protocol=["Reducir alimentación en 25%",
                      "Incrementar aireación 10%",
                      "Medir amonio en 1 hora"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="Amonio en rango",
            message=f"Amonio en {am:.2f} mg/L, dentro del rango seguro (< 0.5)."))

    if nt >= 1.0:
        hallazgos.append(dict(
            severity="crit", title="Acumulación de nitritos (NO₂⁻)",
            message=f"Nitritos en {nt:.2f} mg/L indican conversión incompleta del ciclo del nitrógeno.",
            protocol=["Aumentar recirculación al 90%",
                      "Agregar colonias de Nitrobacter",
                      "Verificar pH (óptimo 6.8–7.5)"]))
    elif nt >= 0.5:
        hallazgos.append(dict(
            severity="warn", title="Nitritos en aumento",
            message=f"Nitritos en {nt:.2f} mg/L, vigilar tendencia.",
            protocol=["Monitorear cada 30 minutos", "Revisar madurez del biofiltro"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="Nitritos en rango",
            message=f"Nitritos en {nt:.2f} mg/L, nivel seguro."))

    if od < 4.0:
        hallazgos.append(dict(
            severity="crit", title="Hipoxia (bajo oxígeno disuelto)",
            message=f"OD en {od:.1f} mg/L, riesgo de estrés o muerte de los peces.",
            protocol=["Llevar aireación al 100%",
                      "Revisar difusores de aire obstruidos",
                      "Reducir carga de alimentación"]))
    elif od < 5.0:
        hallazgos.append(dict(
            severity="warn", title="Oxígeno disuelto bajo",
            message=f"OD en {od:.1f} mg/L, por debajo del óptimo.",
            protocol=["Subir aireación 20%"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="Oxigenación adecuada",
            message=f"Oxígeno disuelto en {od:.1f} mg/L."))

    if flujo < 5.0:
        hallazgos.append(dict(
            severity="crit", title="Fallo de bomba o filtro",
            message=f"Caudal en {flujo:.1f} L/min, muy por debajo de lo esperado.",
            protocol=["Inspeccionar bomba de recirculación",
                      "Limpiar filtro mecánico",
                      "Verificar caudalímetro",
                      "Cortar alimentación mientras dure la falla"]))
    elif flujo < 6.0:
        hallazgos.append(dict(
            severity="warn", title="Caudal reducido",
            message=f"Flujo en {flujo:.1f} L/min, vigilar bomba/filtro.",
            protocol=["Revisar obstrucciones en tuberías"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="Recirculación normal",
            message=f"Caudal en {flujo:.1f} L/min."))

    if temp > 30 or temp < 20:
        hallazgos.append(dict(
            severity="warn", title="Temperatura fuera de rango",
            message=f"Temperatura en {temp:.1f} °C (óptimo 24–28 °C).",
            protocol=["Ajustar calefacción del módulo",
                      "Verificar sondas térmicas"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="Temperatura estable",
            message=f"Temperatura en {temp:.1f} °C."))

    if ph < 6.0 or ph > 8.0:
        hallazgos.append(dict(
            severity="warn", title="pH fuera de rango",
            message=f"pH en {ph:.2f} (óptimo 6.5–7.5).",
            protocol=["Dosificar amortiguador de pH",
                      "Verificar dureza del agua"]))
    else:
        hallazgos.append(dict(
            severity="ok", title="pH estable",
            message=f"pH en {ph:.2f}."))

    criticos = sum(1 for h in hallazgos if h["severity"] == "crit")
    if criticos:
        nivel_general = "crit"
    elif any(h["severity"] == "warn" for h in hallazgos):
        nivel_general = "warn"
    else:
        nivel_general = "ok"

    return {"nivel_general": nivel_general, "hallazgos": hallazgos}