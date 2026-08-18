"""Controlador difuso (mock heurístico).

Contrato de salida listo para conectar backend/ai/fuzzy_controller.py sin tocar la UI.
"""


def control_action(values, setpoints=None):
    sp = setpoints or {}
    od_t = sp.get("od", 6.0)
    temp_t = sp.get("temp", 26.0)

    od = values.get("od", 6.0)
    temp = values.get("temp", 26.0)
    am = values.get("amonio", 0.0)
    nt = values.get("nitrito", 0.0)

    aireacion = 12 + (od_t - od) * 26
    calefaccion = 50 + (temp_t - temp) * 10
    recirculacion = 18 + am * 28 + nt * 22

    return {
        "aireacion": round(min(max(aireacion, 5), 100), 1),
        "calefaccion": round(min(max(calefaccion, 0), 100), 1),
        "recirculacion": round(min(max(recirculacion, 10), 100), 1),
    }


def active_rules(values, setpoints):
    sp = setpoints or {}
    od_t = sp.get("od", 6.0)
    temp_t = sp.get("temp", 26.0)

    od = values.get("od", 6.0)
    temp = values.get("temp", 26.0)
    am = values.get("amonio", 0.0)
    nt = values.get("nitrito", 0.0)

    reglas = []
    if od < od_t:
        reglas.append(f"SI OD = {od:.1f} ES Bajo ENTONCES Aireación = Alto")
    else:
        reglas.append(f"SI OD = {od:.1f} ES Adecuado ENTONCES Aireación = Medio")

    if temp < temp_t:
        reglas.append(f"SI Temperatura = {temp:.1f} ES Fría ENTONCES Calefacción = Alto")
    elif temp > temp_t + 2:
        reglas.append(f"SI Temperatura = {temp:.1f} ES Caliente ENTONCES Calefacción = Bajo")
    else:
        reglas.append(f"SI Temperatura = {temp:.1f} ES Óptima ENTONCES Calefacción = Medio")

    if am > 0.5 or nt > 0.5:
        reglas.append("SI Amonio/Nitritos elevados ENTONCES Recirculación = Alto")
    else:
        reglas.append("SI Amonio/Nitritos bajos ENTONCES Recirculación = Medio")

    return reglas