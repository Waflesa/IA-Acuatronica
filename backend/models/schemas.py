from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ManualOverrideModel(BaseModel):
    """Esquema de validación para entradas manuales enviadas desde el Frontend."""
    temperature: float = Field(..., ge=0, le=50, description="Temperatura en °C")
    dissolved_oxygen: float = Field(..., ge=0, le=20, description="Oxígeno Disuelto en mg/L")
    ammonia: float = Field(..., ge=0, le=10, description="Amonio en mg/L")
    nitrite: Optional[float] = Field(0.0, ge=0, le=10, description="Nitritos en mg/L")
    turbidity: Optional[float] = Field(10.0, ge=0, le=100, description="Turbidez en cm")

class ModeConfigResponse(BaseModel):
    """Respuesta al cambiar el modo de simulación."""
    status: str
    mode: str

class OverrideResponse(BaseModel):
    """Respuesta tras actualizar valores manualmente."""
    status: str
    data: Dict[str, Any]