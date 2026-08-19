# IA-Acuatronica

Sistema de monitoreo y control de un sistema acuapónico con interfaz de escritorio (PySide6) e inteligencia artificial (control fuzzy y sistema experto).

## Estructura

```
IA-Acuatronica/
├── main.py                  # Punto de entrada de la aplicación de escritorio
├── ui/                      # Frontend (PySide6)
│   ├── main_window.py       # Ventana principal (nativa, tema, navegación)
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

La aplicación levanta el backend (FastAPI) automáticamente como subproceso en el puerto `8000` y lo detiene al cerrarse; no hace falta iniciarlo a mano.

## Acceso directo en el escritorio

### Opción 1: Instalador (recomendado)

1. Ejecuta `dist\H2-OBSERVER-Setup.exe`.
2. En el paso **Tareas de instalación**, marca **"Crear acceso directo en el escritorio"**.
3. Al terminar, aparece el acceso directo `H2-OBSERVER` en el escritorio y en el menú Inicio.

### Opción 2: Manual (desde el código fuente)

1. Crea un acceso directo nuevo en el escritorio con el destino:
   `C:\ruta\a\Python\pythonw.exe "C:\ruta\al\proyecto\main.py"`
2. En **Iniciar en** coloca la carpeta del proyecto (la misma de `main.py`).
3. Si quieres el ícono, en **Cambiar icono…** usa `logo.ico` del proyecto.

Con cualquiera de las dos opciones, el doble clic abre la app y arranca el backend en paralelo (la pantalla de carga dura lo que tarda el backend en estar listo más 2 segundos).

## Empaquetar instalador

```bash
packaging\build.bat
```

El instalador se genera en `dist\H2-OBSERVER-Setup.exe`.