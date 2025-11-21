from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

@dataclass
class ExistenciasPaths:
    """
    Paths relacionados con el módulo de existencias.
    Todos se pueden sobreescribir por .env.
    """
    origen_planos: Path
    origen_nacional: Path
    log_dir: Path

@dataclass
class ExistenciasSettings:
    paths: ExistenciasPaths

def get_existencias_settings() -> ExistenciasSettings:
    """
    Carga configuración de existencias desde variables de entorno.

    - En PROD: usas .env para poner las rutas reales (C:\...).
    - En DEV/local/git: usamos defaults relativos a la raíz del repo,
      así no quedan rutas duras en el código.
    """
    # Defaults neutros (no exponemos rutas reales de producción)
    origen_default = ROOT_DIR / "data" / "existencias" / "planos"
    nacional_default = ROOT_DIR / "data" / "existencias" / "nacional"
    log_default = ROOT_DIR / "logs" / "existencias"

    origen = os.getenv("EXISTENCIAS_ORIGEN_DIR", str(origen_default))
    nacional = os.getenv("EXISTENCIAS_NACIONAL_DIR", str(nacional_default))
    log_dir = os.getenv("EXISTENCIAS_LOG_DIR", str(log_default))

    return ExistenciasSettings(
        paths=ExistenciasPaths(
            origen_planos=Path(origen),
            origen_nacional=Path(nacional),
            log_dir=Path(log_dir),
        )
    )

def validate_and_create_dirs(settings: ExistenciasSettings) -> None:
    """Crea directorios necesarios si no existen."""
    dirs_to_create = [
        settings.paths.origen_planos,
        settings.paths.origen_nacional,
        settings.paths.log_dir,
        settings.paths.origen_planos / "GESTIONADOS",
        settings.paths.origen_planos / "ERRORES",
    ]

    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio verificado/creado: {d}")