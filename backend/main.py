import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_engine.dataset_loader import DatasetEngine
from ai.fuzzy_controller import FuzzyAcuaponiaController

app = FastAPI(title="Acuatrónica Core API", version="1.0.0")

# Permitir comunicación fluida con la aplicación Web (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path

# Obtiene la ruta raíz del proyecto (IA-Acuatronica)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "WQD.xlsx"

# Inicialización de motores en el backend
dataset_engine = DatasetEngine(str(DATA_PATH))
fuzzy_controller = FuzzyAcuaponiaController()

# Estado global de la simulación
simulation_config = {
    "mode": "replay",  # Modos disponibles: "replay" | "manual"
    "simulation_speed": 1.0,  # Frecuencia en segundos por lectura
    "manual_override": {}
}

class ManualOverrideModel(BaseModel):
    temperature: float
    dissolved_oxygen: float
    ammonia: float

@app.get("/")
def check_health():
    return {"status": "operational", "system": "Acuaponía Inteligente"}

@app.post("/api/mode/{mode}")
def set_simulation_mode(mode: str):
    """Permite al frontend alternar entre simular datos del dataset o ingresar datos manualmente."""
    if mode in ["replay", "manual"]:
        simulation_config["mode"] = mode
        return {"status": "success", "mode": mode}
    return {"error": "Modo no válido. Use 'replay' o 'manual'."}

@app.post("/api/override")
def set_manual_values(data: ManualOverrideModel):
    """Recibe parámetros directamente desde los controles/sliders de la web."""
    simulation_config["manual_override"] = data.dict()
    simulation_config["mode"] = "manual"
    return {"status": "updated", "data": simulation_config["manual_override"]}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """Canal continuo en tiempo real que emite métricas de sensores y respuestas difusas."""
    await websocket.accept()
    try:
        while True:
            # 1. Obtención de lecturas según el modo activo
            if simulation_config["mode"] == "replay":
                sample = dataset_engine.get_next_sample()
            else:
                sample = simulation_config["manual_override"]

            # Extracción de valores del sample del dataset
            temp = sample.get("temperature", 24.0)
            do = sample.get("dissolved_oxygen", 6.0)
            ammonia = sample.get("ammonia", 0.0)
            nitrite = sample.get("nitrite", 0.0)
            turbidity = sample.get("turbidity", 10.0)

            # Evaluación con las 5 variables
            fuzzy_actuators = fuzzy_controller.evaluate(
            temperature=temp,
            dissolved_oxygen=do,
            ammonia=ammonia,
            nitrite=nitrite,
            turbidity=turbidity
)

            # 3. Empaquetado de telemetría completa
            telemetry_packet = {
                "sensors": sample,
                "actuators": fuzzy_actuators,
                "mode": simulation_config["mode"]
            }

            # 4. Envío al cliente web
            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(simulation_config["simulation_speed"])

    except WebSocketDisconnect:
        print("El cliente web se ha desconectado de la transmisión de telemetría.")