import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.ai.expert_system import WaterExpertSystem
from backend.ai.fuzzy_controller import FuzzyControllerWrapper

app = FastAPI(title="Backend Acuatrónica")

expert_system = WaterExpertSystem()
fuzzy_controller = FuzzyControllerWrapper()

@app.get("/")
def read_root():
    return {"status": "online", "message": "Servidor Acuatrónica en ejecución"}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    print("[SERVER] Cliente WebSocket conectado")
    try:
        while True:
            try:
                # Datos de prueba para telemetría
                sample_sensors = {
                    "temperature": 26.3,
                    "dissolved_oxygen": 6.4,
                    "ammonia": 0.28,
                    "nitrite": 0.22,
                    "ph": 6.92,
                    "turbidity": 25.0
                }

                # 1. Inferencia Lógica Difusa
                actuators = fuzzy_controller.evaluate(
                    temperature=sample_sensors["temperature"],
                    dissolved_oxygen=sample_sensors["dissolved_oxygen"],
                    ammonia=sample_sensors["ammonia"],
                    nitrite=sample_sensors["nitrite"],
                    turbidity=sample_sensors["turbidity"]
                )

                # 2. Diagnóstico Sistema Experto
                diagnosis = expert_system.diagnose(sample_sensors)

                packet = {
                    "sensors": sample_sensors,
                    "actuators": actuators,
                    "diagnosis": diagnosis,
                    "mode": "simulation"
                }

                await websocket.send_json(packet)
                await asyncio.sleep(2)

            except Exception as e:
                # Captura errores internos sin tumbar la conexión del cliente
                print(f"[ERROR EN TELEMETRÍA]: {e}")
                await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("[SERVER] Cliente WebSocket desconectado")