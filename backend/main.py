import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.ai.expert_system import WaterExpertSystem
from backend.ai.fuzzy_controller import FuzzyControllerWrapper
from backend.data_engine.dataset_loader import DatasetEngine

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Data" / "WQD_Limpio.csv"

app = FastAPI(title="Backend Acuatrónica")

dataset_engine = DatasetEngine(str(DATA_PATH))
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
                # 0. Muestreo del dataset real de calidad de agua
                sample_sensors = dataset_engine.get_next_sample()
                if not sample_sensors:
                    await asyncio.sleep(2)
                    continue

                # 1. Inferencia Lógica Difusa
                actuators = fuzzy_controller.evaluate(
                    temperature=sample_sensors["temperature"],
                    dissolved_oxygen=sample_sensors["dissolved_oxygen"],
                    ammonia=sample_sensors["ammonia"],
                    nitrite=sample_sensors["nitrite"],
                    turbidity=sample_sensors["turbidity"]
                )

                # 2. Diagnóstico Sistema Experto (ML + motor de reglas)
                diagnosis = expert_system.diagnose(sample_sensors)

                packet = {
                    "sensors": sample_sensors,
                    "actuators": actuators,
                    "diagnosis": diagnosis,
                    "mode": "dataset"
                }

                await websocket.send_json(packet)
                await asyncio.sleep(2)

            except Exception as e:
                # Captura errores internos sin tumbar la conexión del cliente
                print(f"[ERROR EN TELEMETRÍA]: {e}")
                await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("[SERVER] Cliente WebSocket desconectado")