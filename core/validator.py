import openpyxl
import os
from pathlib import Path
from config import COLUMNAS_ENTRADA

class ValidadorArchivo:
    def validar(self, filepath: str, banco: str = "BHD"):
        """
        Valida que el archivo cumple con las condiciones para el banco seleccionado.
        Retorna (es_valido, mensaje_error, datos)
        """
        if not str(filepath).lower().endswith('.xlsx'):
            return False, "El archivo seleccionado no es un archivo Excel (.xlsx).", None
            
        # Verificar si está abierto
        try:
            temp_path = filepath + ".tmp_check"
            os.rename(filepath, temp_path)
            os.rename(temp_path, filepath)
        except OSError:
            return False, "El archivo está abierto en otro programa. Ciérrelo e intente nuevamente.", None
            
        try:
            wb = openpyxl.load_workbook(filepath, data_only=True)
            ws = wb.active
        except Exception as e:
            return False, f"El archivo está dañado o no se pudo abrir: {str(e)}", None
            
        # Buscar la fila de headers (buscando 'NUMERO PST')
        header_row = -1
        pst_col = -1
        
        for row in range(1, min(ws.max_row + 1, 30)): # Buscar en las primeras 30 filas
            for col in range(1, ws.max_column + 1):
                val = ws.cell(row=row, column=col).value
                if val and isinstance(val, str) and 'NUMERO PST' in val.upper():
                    header_row = row
                    pst_col = col
                    break
            if header_row != -1:
                break
                
        if header_row == -1:
            return False, "La estructura del archivo exportado ha cambiado. No se encontró la columna 'NUMERO PST'. Verifique que el archivo provenga del sistema correcto.", None
            
        # Extraer nombres de las columnas en esa fila
        columnas_encontradas = []
        col_indices = {}
        for col in range(1, ws.max_column + 1):
            val = ws.cell(row=header_row, column=col).value
            if val and isinstance(val, str):
                columnas_encontradas.append(val.strip())
                col_indices[val.strip()] = col
                
        # Validar columnas faltantes según el banco
        if banco == "BANRESERVAS":
            cols_requeridas = ['CTA. A DEBITAR', 'CTA. A CREDITAR', 'DESEMBOLSO', 'NO. DESEMBOLSO', 'NUMERO PST', 'NOMBRE**']
        else:
            cols_requeridas = ['CEDULA', 'NOMBRE**', 'DESEMBOLSO', 'NUMERO PST']

        columnas_faltantes = []
        for col in cols_requeridas:
            if col not in columnas_encontradas:
                columnas_faltantes.append(col)
                
        if columnas_faltantes:
            return False, f"Faltan las siguientes columnas requeridas para {banco}:\n{', '.join(columnas_faltantes)}", None
            
        # Extraer registros y buscar duplicados
        data_start_row = header_row + 1
        data_end_row = data_start_row
        
        numeros_pst = set()
        duplicados = set()
        num_registros = 0
        
        for row in range(data_start_row, ws.max_row + 1):
            pst_val = ws.cell(row=row, column=col_indices['NUMERO PST']).value
            if not pst_val:
                break # Encontramos el final de los datos
                
            num_registros += 1
            data_end_row = row
            
            pst_str = str(pst_val).strip()
            if pst_str in numeros_pst:
                duplicados.add(pst_str)
            numeros_pst.add(pst_str)
            
        if num_registros == 0:
            return False, "El archivo seleccionado no contiene registros.", None
            
        if duplicados:
            return False, f"Se encontraron préstamos duplicados. Corrija el archivo antes de continuar.\nDuplicados: {', '.join(duplicados)}", None
            
        datos = {
            'header_row': header_row,
            'data_start_row': data_start_row,
            'data_end_row': data_end_row,
            'num_registros': num_registros,
            'col_indices': col_indices,
            'duplicados': list(duplicados)
        }
        
        wb.close()
        return True, "Archivo válido", datos
