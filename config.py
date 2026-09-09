import json
from pathlib import Path

# --- Directorio base del proyecto ---
# Esta línea detecta automáticamente en qué carpeta está guardado el proyecto
CARPETA_APP = Path(__file__).resolve().parent
CONFIG_JSON_PATH = CARPETA_APP / "config.json"

def obtener_carpetas_salida() -> dict:
    if CONFIG_JSON_PATH.exists():
        try:
            with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Soporta tanto el formato antiguo como el nuevo por banco
                ruta_bhd = data.get("BHD") or data.get("CARPETA_SALIDA") or str(CARPETA_APP)
                ruta_reservas = data.get("BANRESERVAS") or str(CARPETA_APP)
                return {
                    "BHD": Path(ruta_bhd),
                    "BANRESERVAS": Path(ruta_reservas)
                }
        except Exception as e:
            print(f"Error al leer configuración por bancos: {e}")
    return {
        "BHD": CARPETA_APP,
        "BANRESERVAS": CARPETA_APP
    }

def obtener_carpeta_salida() -> Path:
    return obtener_carpetas_salida()["BHD"]

def guardar_carpeta_salida(nueva_ruta: Path) -> None:
    guardar_carpeta_salida_banco("BHD", nueva_ruta)

def guardar_carpeta_salida_banco(banco: str, nueva_ruta: Path) -> None:
    try:
        data = {}
        if CONFIG_JSON_PATH.exists():
            try:
                with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[banco] = str(nueva_ruta)
        if banco == "BHD":
            data["CARPETA_SALIDA"] = str(nueva_ruta)
            
        with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar configuración para {banco}: {e}")

# Carga inicial (mantenemos compatibilidad con imports directos de CARPETA_SALIDA)
CARPETA_SALIDA = obtener_carpeta_salida()

# --- Carpetas adicionales ---
CARPETA_REGISTROS = CARPETA_APP / "Control de Préstamos"
CARPETA_LOGS = CARPETA_APP / "logs"

# --- Plantilla base ---
PLANTILLA_EXCEL_PATH = CARPETA_APP / "(USA ESTE EXCEL) MUESTRA DE CARGA COLOCACION BHD.xlsx"

# --- Plantilla del archivo de salida ---
NOMBRE_SALIDA_TEMPLATE = "MUESTRA DE CARGA COLOCACION BHD {fecha}.xlsx"

# --- Columnas de entrada (Fila 9) ---
COLUMNAS_ENTRADA = [
    'CTA. A DEBITAR',
    'FONDO A DEBITAR',
    'CTA. A CREDITAR',
    'NUMERO PST',
    'NOMBRE**',
    'CEDULA',
    'NO. DESEMBOLSO',
    'MONTO',
    'TRAMITES',
    'MONTO REFINANCIADO',
    'DESEMBOLSO',
    'CODIGO SUCURSAL'
]

# --- Columnas de salida ---
COLUMNAS_SALIDA = [
    'Tipo de identificación',
    'Número de identificación',
    'Beneficiario',
    'Monto',
    'Número único',
    'Fecha de efectividad',
    'Concepto',
    'Tipo de registro',
    'Correo del beneficiario'
]

# --- Configuración de protección ---
COLUMNAS_BLOQUEADAS = {'B', 'C', 'D', 'E'}
COLUMNAS_EDITABLES  = {'A', 'F', 'G', 'H', 'I'}
CONTRASENA_PROTECCION = None

# --- Valores Fijos ---
TIPO_IDENTIFICACION = 'C'
CONCEPTO = 'Desembolso Prestamos MUDE'
TIPO_REGISTRO = 'I'
CORREO_BENEFICIARIO = 'ejemplo@correo.com'

# --- Columnas del registro mensual ---
COLUMNAS_REGISTRO = [
    'Fecha',
    'Hora',
    'Número de préstamo',
    'Nombre',
    'Archivo generado'
]

# --- Meses en español ---
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# --- Formatos Excel ---
ANCHOS_COLUMNA_SALIDA = {
    'A': 19.86, 'B': 24.86, 'C': 22.0,  'D': 14.0,
    'E': 16.0,  'F': 18.0,  'G': 28.14, 'H': 14.0,
    'I': 23.0
}
ALTURA_FILA_DATOS = 15.75
