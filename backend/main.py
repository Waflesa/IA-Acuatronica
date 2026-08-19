import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.ai.expert_system import WaterExpertSystem
from backend.ai.fuzzy_controller import FuzzyControllerWrapper

app = FastAPI(title="Backend Acuatrónica")

expert_system = WaterExpertSystem()
fuzzy_controller = FuzzyControllerWrapper()

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Lectura simulated o de dataset
            sample_sensors = {
                "temperature": 29.5,
                "dissolved_oxygen": 2.1,
                "ammonia": 0.62,
                "nitrite": 0.8,
                "ph": 6.8,
                "turbidity": 45.0,
                "bod": 5.2,
                "co2": 8.3,
                "alkalinity": 90.0,
                "hardness": 110.0,
                "calcium": 60.0,
                "phosphorus": 1.0,
                "h2s": 0.02,
                "plankton": 3500.0
            }

            # 1. Evaluación Fuzzy
            actuators = fuzzy_controller.evaluate(
                temperature=sample_sensors["temperature"],
                dissolved_oxygen=sample_sensors["dissolved_oxygen"],
                ammonia=sample_sensors["ammonia"],
                nitrite=sample_sensors["nitrite"],
                turbidity=sample_sensors["turbidity"]
            )

            # 2. Evaluación Experta + Random Forest
            diagnosis = expert_system.diagnose(sample_sensors)

            # 3. Enviar paquete al frontend PySide6
            packet = {
                "sensors": sample_sensors,
                "actuators": actuators,
                "diagnosis": diagnosis,
                "mode": "simulation"
            }

            await websocket.send_json(packet)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Cliente Qt desconectado")