class MotorInferenciaAcuatronica:
    def __init__(self):
        self.hechos = {}
        self.reglas = []

    def agregar_hecho(self, variable, valor):
        self.hechos[variable] = valor

    def agregar_regla(self, condiciones, conclusion, valor_conclusion):
        self.reglas.append({
            "condiciones": condiciones,
            "conclusion": conclusion,
            "valor_conclusion": valor_conclusion
        })

    def ejecutar(self):
        print("=== DIAGNOSTICO DEL MODULO ACUAPONICO ===")
        cambios = True

        while cambios:
            cambios = False
            for regla in self.reglas:
                conclusion = regla["conclusion"]
                if conclusion in self.hechos:
                    continue

                se_cumplen = True
                for variable, valor_esperado in regla["condiciones"].items():
                    valor_actual = self.hechos.get(variable)

                    if type(valor_esperado) is str and valor_esperado.startswith(">"):
                        limite = float(valor_esperado[1:])
                        if valor_actual is None or valor_actual <= limite:
                            se_cumplen = False
                            break
                    elif type(valor_esperado) is str and valor_esperado.startswith("<"):
                        limite = float(valor_esperado[1:])
                        if valor_actual is None or valor_actual >= limite:
                            se_cumplen = False
                            break
                    elif valor_actual != valor_esperado:
                        se_cumplen = False
                        break

                if se_cumplen:
                    self.agregar_hecho(conclusion, regla["valor_conclusion"])
                    print(f" [DIAGNOSTICO] Regla activada por {regla['condiciones']}")
                    print(f"   >> {conclusion} = {regla['valor_conclusion']}")
                    cambios = True

        return self.hechos


# Estos umbrales son de referencia, se pueden ajustar segun la especie
UMBRAL_AMONIO = 0.5
UMBRAL_NITRITO = 2.5
UMBRAL_DO_BAJO = 3.0


def evaluar_toxicidad_amonio(amonio: float) -> bool:
    return amonio > UMBRAL_AMONIO


def evaluar_toxicidad_nitrito(nitrito: float) -> bool:
    return nitrito > UMBRAL_NITRITO


def evaluar_falla_aireacion(oxigeno_disuelto: float) -> bool:
    return oxigeno_disuelto < UMBRAL_DO_BAJO


def construir_base_conocimiento(motor: MotorInferenciaAcuatronica) -> None:
    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": True, "alerta_toxicidad_nitrito": True},
        conclusion="protocolo_mitigacion",
        valor_conclusion="EMERGENCIA: cambio parcial de agua urgente + revision del biofiltro"
    )

    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": True, "alerta_toxicidad_nitrito": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Reducir alimentacion + aumentar recirculacion para diluir amonio"
    )

    motor.agregar_regla(
        condiciones={"alerta_toxicidad_nitrito": True, "alerta_toxicidad_amonio": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Anadir sal aclimatada + monitorear ciclo de nitrificacion"
    )

    motor.agregar_regla(
        condiciones={"posible_falla_aireacion": True, "alerta_toxicidad_amonio": False,
                     "alerta_toxicidad_nitrito": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Falla mecanica probable: activar aireador de respaldo + revisar bomba/filtro"
    )

    motor.agregar_regla(
        condiciones={"alerta_toxicidad_amonio": False, "alerta_toxicidad_nitrito": False,
                     "posible_falla_aireacion": False},
        conclusion="protocolo_mitigacion",
        valor_conclusion="Parametros dentro de rango: monitoreo estandar"
    )


if __name__ == "__main__":
    lectura_sensores = {
        "amonio": 0.75,
        "nitrito": 1.2,
        "oxigeno_disuelto": 5.4,
    }

    motor = MotorInferenciaAcuatronica()
    construir_base_conocimiento(motor)

    motor.agregar_hecho("alerta_toxicidad_amonio", evaluar_toxicidad_amonio(lectura_sensores["amonio"]))
    motor.agregar_hecho("alerta_toxicidad_nitrito", evaluar_toxicidad_nitrito(lectura_sensores["nitrito"]))
    motor.agregar_hecho("posible_falla_aireacion", evaluar_falla_aireacion(lectura_sensores["oxigeno_disuelto"]))

    resultado = motor.ejecutar()

    print("\n--- REPORTE DE DIAGNOSTICO ---")
    print(f"Protocolo a aplicar: {resultado.get('protocolo_mitigacion', 'Sin diagnostico')}")
