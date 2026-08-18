# IA-Acuatronica

Sistema de monitoreo y control de un sistema acuapónico con interfaz de escritorio (PySide6) e inteligencia artificial (control fuzzy y sistema experto).

## Estructura

```
IA-Acuatronica/
├── main.py                  # Punto de entrada de la aplicación de escritorio
├── ui/                      # Frontend (PySide6)
│   ├── main_window.py       # Ventana principal (frameless, tema, navegación)
│   ├── app_theme.py         # Paleta y tema claro/oscuro
│   ├── splash.py            # Pantalla de carga
│   ├── paths.py             # Rutas de recursos (dev / empaquetado)
│   ├── widgets/             # Componentes reutilizables (gauges, charts, cards...)
│   ├── pages/               # Páginas de la aplicación (dashboard, fuzzy, alertas...)
│   └── logic/               # Lógica del frontend (sensores, fuzzy, sistema experto)
├── backend/                 # Backend (FastAPI + IA)
│   ├── main.py              # API + WebSockets
│   ├── ai/                  # Control fuzzy y sistema experto
│   ├── data_engine/         # Carga del dataset
│   └── models/              # Esquemas (Pydantic)
├── packaging/               # Herramientas de empaquetado
│   ├── build.bat            # Genera el instalador (PyInstaller + Inno Setup)
│   ├── build_app.py
│   └── installer.iss
├── resources/               # Recursos gráficos y fuentes
├── Data/                    # Datasets
├── styles_dark.qss          # Estilos del tema oscuro
├── styles_light.qss         # Estilos del tema claro
└── requirements.txt         # Dependencias
```

## Ejecutar

```bash
pip install -r requirements.txt
python main.py
```

## Empaquetar instalador

```bash
packaging\build.bat
```

El instalador se genera en `dist\H2-OBSERVER-Setup.exe`.