"""
Constantes del dominio de Existencias.

Este archivo centraliza todos los números "mágicos" y strings hardcodeados
que aparecen en el código, para facilitar mantenimiento y evitar errores.
"""

# ==================== ESTRUCTURA DE ARCHIVOS ====================

class NomenclaturaArchivo:
    """
    Constantes relacionadas con la estructura del nombre de archivo.
    
    Formato: VYBU<IATA><YYMMDD><HHMI><TV>.TXT
    Ejemplo: VYBUBOG2511210750CU.TXT
    
    Posiciones (0-indexed):
        0-3:   VYBU (prefijo fijo de la empresa)
        4-6:   BOG (código IATA ciudad - 3 letras)
        7-12:  251121 (fecha yymmdd - 6 dígitos)
        13-16: 0750 (hora HHMM - 4 dígitos)
        17-18: CU (tipo de valor - 2 letras)
    """
    
    # Longitudes
    PREFIJO_LEN = 4        # "VYBU"
    IATA_LEN = 3           # Código ciudad (BOG, CTG, MDE, etc.)
    FECHA_LEN = 6          # yymmdd
    HORA_LEN = 4           # HHMM
    TIPO_VALOR_LEN = 2     # CU, EU, DA, etc.
    
    # Posiciones de inicio (0-indexed)
    PREFIJO_START = 0
    IATA_START = PREFIJO_LEN                    # 4
    FECHA_START = PREFIJO_LEN + IATA_LEN        # 7
    HORA_START = FECHA_START + FECHA_LEN        # 13
    TIPO_VALOR_START = HORA_START + HORA_LEN    # 17
    
    # Posiciones de fin (0-indexed, exclusivo)
    PREFIJO_END = PREFIJO_START + PREFIJO_LEN   # 4
    IATA_END = IATA_START + IATA_LEN            # 7
    FECHA_END = FECHA_START + FECHA_LEN         # 13
    HORA_END = HORA_START + HORA_LEN            # 17
    TIPO_VALOR_END = TIPO_VALOR_START + TIPO_VALOR_LEN  # 19
    
    # Valores fijos
    PREFIJO_EMPRESA = "VYBU"
    CIUDAD_NACIONAL = "BOG"  # Archivos nacionales siempre son de Bogotá
    EXTENSION = ".TXT"


# ==================== ESTRUCTURA DE REGISTROS ====================

class TiposRegistro:
    """
    Tipos de registro en archivos de existencias.
    """
    HEADER = "01"   # Cabecera (una por archivo)
    DETALLE = "02"  # Detalle de denominaciones (N por archivo)


class LongitudesRegistro:
    """
    Longitudes mínimas de campos en registros CSV.
    """
    MIN_CAMPOS_HEADER = 11   # Registro 01 tiene 11 campos
    MIN_CAMPOS_DETALLE = 21  # Registro 02 tiene mínimo 21 campos (5 fijos + 16 denoms)


class EstructuraDetalle:
    """
    Constantes relacionadas con el registro 02 (detalle).
    """
    MAX_DENOMINACIONES = 8  # Máximo 8 pares de valor/cantidad
    CAMPOS_FIJOS = 5        # tipo_reg, cod_tipo_valor, nombre, cod_calidad, nombre_calidad
    CAMPOS_POR_DENOMINACION = 2  # (valor, cantidad)
    TOTAL_CAMPOS_DENOMINACIONES = MAX_DENOMINACIONES * CAMPOS_POR_DENOMINACION  # 16


# ==================== FORMATOS DE FECHA ====================

class FormatosFecha:
    """
    Formatos de fecha usados en diferentes contextos.
    """
    # Entrada (archivos origen)
    YYMMDD = "%y%m%d"           # 251121 → 2025-11-21
    DDMMYYYY_SLASH = "%d/%m/%Y" # 21/11/2025
    
    # Salida (archivos nacionales)
    DDMMYYYY_OUTPUT = "%d/%m/%Y"  # 21/11/2025 (con barras)
    
    # Timestamps
    YYMMDDHHMM = "%y%m%d%H%M"     # 2511210750
    TIMESTAMP_BACKUP = "%Y%m%dT%H%M"  # 20251121T0930


# ==================== CÓDIGOS DE DIVISA ====================

class CodigosDivisa:
    """
    Códigos numéricos de divisas/tipos de valor.
    """
    CU = 1   # Peso colombiano (billetes)
    CB = 2   # Peso colombiano (monedas)
    DA = 3   # Dólar americano
    DC = 4   # Dólar canadiense
    FF = 5
    MA = 6
    FS = 7
    YJ = 8
    LE = 9
    CH = 14
    EU = 24  # Euro
    SD = 51


# ==================== CÓDIGOS DE CALIDAD ====================

class CodigosCalidad:
    """
    Códigos de calidad del billete.
    """
    BUEN_ESTADO = 2
    DETERIORADO = 23
    # Agregar más según especificación del cliente


# ==================== CARPETAS DEL SISTEMA ====================

class NombresCarpetas:
    """
    Nombres estándar de carpetas del sistema.
    """
    PLANOS = "PLANOS"
    NACIONAL = "NACIONAL"
    GESTIONADOS = "GESTIONADOS"
    ERRORES = "ERRORES"
    COPIAS = "COPIAS"
    LOGS = "logs"


# ==================== VALIDACIÓN ====================

class Validacion:
    """
    Constantes para validaciones.
    """
    MAX_TAMANIO_ARCHIVO_MB = 10  # Tamaño máximo de archivo a procesar
    MIN_REGISTROS_DETALLE = 1    # Mínimo 1 registro 02 por archivo
    MAX_REGISTROS_DETALLE = 100  # Máximo razonable de registros 02


# ==================== ENCODING ====================

class Encoding:
    """
    Configuraciones de encoding para archivos.
    """
    DEFAULT = "utf-8"
    ERRORS = "ignore"  # Ignorar caracteres no UTF-8
    NEWLINE = "\n"     # Salto de línea Unix