import os
from pathlib import Path
from datetime import datetime
from config import NOMBRE_SALIDA_TEMPLATE, obtener_carpeta_salida

class GestorArchivos:
    def generar_ruta_salida(self, carpeta_destino: Path = None) -> Path:
        """
        Genera la ruta de salida con la fecha de hoy para BHD (formato Excel).
        Si el archivo ya existe, añade (1), (2), etc.
        """
        if carpeta_destino is None:
            carpeta_destino = obtener_carpeta_salida()
            
        if not carpeta_destino.exists():
            carpeta_destino.mkdir(parents=True, exist_ok=True)
            
        fecha_hoy = datetime.now().strftime("%d %m %Y")
        nombre_base = NOMBRE_SALIDA_TEMPLATE.format(fecha=fecha_hoy)
        ruta_base = carpeta_destino / nombre_base
        
        if not ruta_base.exists():
            return ruta_base
            
        # Versionado si existe
        contador = 1
        nombre_sin_ext = ruta_base.stem
        ext = ruta_base.suffix
        
        while True:
            nueva_ruta = carpeta_destino / f"{nombre_sin_ext} ({contador}){ext}"
            if not nueva_ruta.exists():
                return nueva_ruta
            contador += 1
            
    def generar_ruta_salida_txt(self, carpeta_destino: Path = None) -> Path:
        """
        Genera la ruta de salida con la fecha de hoy para Banreservas (formato TXT).
        Formato de fecha: "D M AAAA" (ej. "20 7 2026").
        Si el archivo ya existe, añade (1), (2), etc.
        """
        if carpeta_destino is None:
            from config import obtener_carpetas_salida
            carpeta_destino = obtener_carpetas_salida()["BANRESERVAS"]
            
        if not carpeta_destino.exists():
            carpeta_destino.mkdir(parents=True, exist_ok=True)
            
        now = datetime.now()
        fecha_str = f"{now.day} {now.month} {now.year}"
        nombre_base = f"MUESTRA DE CARGA BANRESERVAS {fecha_str}.txt"
        ruta_base = carpeta_destino / nombre_base
        
        if not ruta_base.exists():
            return ruta_base
            
        # Versionado si existe
        contador = 1
        nombre_sin_ext = ruta_base.stem
        ext = ruta_base.suffix
        
        while True:
            nueva_ruta = carpeta_destino / f"{nombre_sin_ext} ({contador}){ext}"
            if not nueva_ruta.exists():
                return nueva_ruta
            contador += 1
            
    def guardar(self, workbook, ruta_salida: Path) -> Path:
        """
        Guarda el workbook en la ruta especificada.
        """
        workbook.save(ruta_salida)
        return ruta_salida

    def guardar_txt(self, lineas_texto: list, ruta_salida: Path) -> Path:
        """
        Guarda la lista de líneas en un archivo de texto plano.
        """
        with open(ruta_salida, "w", encoding="utf-8") as f:
            for linea in lineas_texto:
                f.write(linea + "\n")
        return ruta_salida
