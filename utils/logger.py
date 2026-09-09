import logging
import os
from datetime import datetime
from config import CARPETA_LOGS

_logger = None

def iniciar_log(archivo_entrada: str):
    global _logger
    
    if not CARPETA_LOGS.exists():
        CARPETA_LOGS.mkdir(parents=True, exist_ok=True)
        
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    archivo_log = CARPETA_LOGS / f"log_{fecha_hoy}.txt"
    
    # Configurar logger
    _logger = logging.getLogger("AutomatizadorColocaciones")
    _logger.setLevel(logging.INFO)
    
    # Limpiar handlers si existen
    if _logger.hasHandlers():
        _logger.handlers.clear()
        
    handler = logging.FileHandler(archivo_log, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    
    _logger.info(f"--- INICIO DE PROCESAMIENTO ---")
    _logger.info(f"Archivo de entrada seleccionado: {archivo_entrada}")

def log_info(mensaje: str):
    if _logger:
        _logger.info(mensaje)

def log_error(mensaje: str):
    if _logger:
        _logger.error(mensaje)

def finalizar_log(tiempo_total: float, archivo_generado: str = None):
    if _logger:
        if archivo_generado:
            _logger.info(f"Archivo generado correctamente: {archivo_generado}")
        _logger.info(f"Tiempo total: {tiempo_total:.2f} segundos.")
        _logger.info(f"--- FIN DE PROCESAMIENTO ---\n")
