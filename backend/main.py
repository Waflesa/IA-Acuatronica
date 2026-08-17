import asyncio
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from data_engine.dataset_loader import DatasetEngine
from ai.fuzzy_controller import FuzzyAcuaponiaController
from ai.expert_system import WaterExpertSystem
from models.schemas import ManualOverrideModel, ModeConfigResponse, OverrideResponse

app = FastAPI(title="Acuatrónica Core API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definición de rutas absolutas
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "WQD.xlsx"

# Inicialización de componentes
dataset_engine = DatasetEngine(str(DATA_PATH))
fuzzy_controller = FuzzyAcuaponiaController()
expert_system = WaterExpertSystem()

# Configuración global e historial
simulation_config = {
    "mode": "replay",
    "simulation_speed": 1.0,  # Frecuencia en segundos
    "paused": False,
    "manual_override": {}
}

event_history: List[Dict[str, Any]] = []

@app.get("/")
def check_health():
    return {"status": "operational", "system": "Acuaponía Inteligente"}

@app.post("/api/mode/{mode}", response_model=ModeConfigResponse)
def set_simulation_mode(mode: str):
    if mode in ["replay", "manual"]:
        simulation_config["mode"] = mode
        return {"status": "success", "mode": mode}
    return {"status": "error", "mode": simulation_config["mode"]}

@app.post("/api/override", response_model=OverrideResponse)
def set_manual_values(data: ManualOverrideModel):
    simulation_config["manual_override"] = data.model_dump()
    simulation_config["mode"] = "manual"
    return {"status": "updated", "data": simulation_config["manual_override"]}

@app.get("/api/history")
def get_event_history():
    """Retorna los últimos 50 eventos grabados en la bitácora."""
    return event_history[-50:]

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not simulation_config["paused"]:
                # 1. Muestreo de datos
                if simulation_config["mode"] == "replay":
                    sample = dataset_engine.get_next_sample()
                else:
                    sample = simulation_config["manual_override"]

                # 2. Evaluación Difusa (Actuadores)
                fuzzy_actuators = fuzzy_controller.evaluate(
                    temperature=sample.get("temperature", 24.0),
                    dissolved_oxygen=sample.get("dissolved_oxygen", 6.0),
                    ammonia=sample.get("ammonia", 0.0),
                    nitrite=sample.get("nitrite", 0.0),
                    turbidity=sample.get("turbidity", 10.0)
                )

                # 3. Evaluación del Sistema Experto (Diagnóstico)
                diagnosis = expert_system.diagnose(sample)

                # 4. Paquete de Telemetría Completo
                telemetry_packet = {
                    "sensors": sample,
                    "actuators": fuzzy_actuators,
                    "diagnosis": diagnosis,
                    "mode": simulation_config["mode"]
                }

                # Registrar en el historial si hay alertas activas
                if diagnosis["alerts"]:
                    event_history.append(telemetry_packet)

                # 5. Envío al cliente web
                await websocket.send_json(telemetry_packet)

            await asyncio.sleep(simulation_config["simulation_speed"])

    except WebSocketDisconnect:
        print("Cliente WebSocket desconectado.")