"""
Utilidades para manejo de rutas - RPA DIAN
Funciones para convertir y manejar rutas relativas al proyecto
"""

import os
from pathlib import Path
from typing import Union

def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto
    
    Returns:
        Path: Ruta absoluta al directorio raíz del proyecto
    """
    # Buscar desde el archivo actual hacia arriba hasta encontrar main.py
    current_path = Path(__file__).resolve()
    
    # Subir directorios hasta encontrar main.py
    for parent in current_path.parents:
        if (parent / "main.py").exists():
            return parent
    
    # Si no encuentra main.py, usar el directorio padre de src/
    return current_path.parent.parent

def get_absolute_path(relative_path: Union[str, Path]) -> str:
    """
    Convierte una ruta relativa al proyecto en ruta absoluta
    
    Args:
        relative_path: Ruta relativa al directorio raíz del proyecto
        
    Returns:
        str: Ruta absoluta con separadores normalizados
    """
    project_root = get_project_root()
    absolute_path = project_root / relative_path
    # Normalizar con separadores forward slash para compatibilidad
    return str(absolute_path.resolve()).replace('\\', '/')

def get_config_path(filename: str = "VariablesGlobales.json") -> str:
    """
    Obtiene la ruta absoluta a un archivo en la carpeta config
    
    Args:
        filename: Nombre del archivo en la carpeta config
        
    Returns:
        str: Ruta absoluta al archivo de configuración
    """
    return get_absolute_path(f"config/{filename}")

def get_downloads_path() -> str:
    """
    Obtiene la ruta absoluta a la carpeta Downloads del usuario
    
    Returns:
        str: Ruta absoluta a Downloads
    """
    home = Path.home()
    return str(home / "Downloads")

def get_documents_dian_path() -> str:
    """
    Obtiene la ruta absoluta a la carpeta de logs DIAN en Documents
    
    Returns:
        str: Ruta absoluta a la carpeta de logs DIAN
    """
    home = Path.home()
    return str(home / "Documents" / "Archivos Excel DIAN")

def ensure_directory_exists(path: Union[str, Path]) -> None:
    """
    Asegura que un directorio existe, creándolo si es necesario
    
    Args:
        path: Ruta al directorio
    """
    Path(path).mkdir(parents=True, exist_ok=True)

# Funciones de conveniencia para rutas comunes del proyecto
def get_config_dir() -> str:
    """Ruta al directorio config"""
    return get_absolute_path("config")

def get_src_dir() -> str:
    """Ruta al directorio src"""
    return get_absolute_path("src")

def get_logs_dir() -> str:
    """Ruta al directorio de logs en Documents del usuario"""
    return get_documents_dian_path()

if __name__ == "__main__":
    # Pruebas de las funciones
    print(f"Raíz del proyecto: {get_project_root()}")
    print(f"Config: {get_config_dir()}")
    print(f"Src: {get_src_dir()}")
    print(f"VariablesGlobales.json: {get_config_path()}")
    print(f"Downloads: {get_downloads_path()}")
    print(f"Logs DIAN: {get_logs_dir()}")