"""
Utilidades para manipulación de texto.
"""
import unicodedata
from pathlib import Path
import logging
import chardet

logger = logging.getLogger(__name__)

def detectar_encoding(archivo: Path) -> str:
    """
    Detecta automáticamente el encoding de un archivo.
    
    Args:
        archivo: Ruta del archivo a analizar
        
    Returns:
        Nombre del encoding detectado (ej: 'utf-8', 'windows-1252', 'ascii')
        
    Example:
        >>> encoding = detectar_encoding(Path("archivo.txt"))
        >>> print(encoding)
        'windows-1252'
    """
    try:
        with archivo.open('rb') as f:
            raw_data = f.read(10000)

        resultado = chardet.detect(raw_data)
        encoding = resultado['encoding']
        confidence = resultado['confidence']

        logger.debug(
            f"Encoding detectado para {archivo.name}: {encoding} "
            f"(confianza: {confidence:.2%})"
        )

        if encoding:
            encoding_lower = encoding.lower()

            # ANSI en Windows es típicamente windows-1252 (Latin-1)
            if encoding_lower in ('ascii', 'windows-1252', 'iso-8859-1', 'latin-1'):
                return 'windows-1252'  # ANSI de Windows

            if 'utf-8' in encoding_lower:
                return 'utf-8'

            return encoding

        logger.warning(f"No se pudo detectar encoding para {archivo.name}, usando utf-8")
        return 'utf-8'

    except Exception as e:
        logger.error(f"Error detectando encoding de {archivo.name}: {e}")
        return 'utf-8'

def leer_archivo_con_encoding_auto(archivo: Path) -> str:
    """
    Lee un archivo detectando automáticamente su encoding.
    
    Intenta:
    1. Detectar encoding con chardet
    2. Leer con encoding detectado
    3. Si falla, intenta con utf-8
    4. Si falla, intenta con windows-1252 (ANSI)
    5. Si todo falla, lee ignorando errores
    
    Args:
        archivo: Ruta del archivo a leer
        
    Returns:
        Contenido del archivo como string
        
    Raises:
        ValueError: Si el archivo no se puede leer de ninguna forma
    """
    try:
        encoding = detectar_encoding(archivo)
        with archivo.open('r', encoding=encoding, errors='strict') as f:
            contenido = f.read()
        logger.info(f"Archivo {archivo.name} leído con encoding: {encoding}")
        return contenido
    except Exception as e:
        logger.warning(f"Fallo lectura con encoding detectado ({encoding}): {e}")
    
    # 2. Intentar con UTF-8
    try:
        with archivo.open('r', encoding='utf-8', errors='strict') as f:
            contenido = f.read()
        logger.info(f"Archivo {archivo.name} leído con UTF-8")
        return contenido
    except Exception as e:
        logger.warning(f"Fallo lectura UTF-8: {e}")
    
    # 3. Intentar con Windows-1252 (ANSI)
    try:
        with archivo.open('r', encoding='windows-1252', errors='strict') as f:
            contenido = f.read()
        logger.info(f"Archivo {archivo.name} leído con Windows-1252 (ANSI)")
        return contenido
    except Exception as e:
        logger.warning(f"Fallo lectura Windows-1252: {e}")
    
    # 4. Última opción: leer ignorando errores
    try:
        with archivo.open('r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()
        logger.warning(
            f"Archivo {archivo.name} leído con UTF-8 ignorando errores. "
            f"Algunos caracteres pueden haberse perdido."
        )
        return contenido
    except Exception as e:
        logger.error(f"No se pudo leer el archivo {archivo.name}: {e}")
        raise ValueError(f"No se pudo leer el archivo {archivo.name}") from e


def limpiar_caracteres_especiales(texto: str) -> str:
    """
    Limpia caracteres especiales de un texto.
    
    Convierte:
    - Vocales acentuadas → sin acento (á→a, é→e, etc.)
    - ñ → n
    - Ñ → N
    - Mantiene espacios y otros caracteres ASCII
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto sin caracteres especiales
        
    Example:
        >>> limpiar_caracteres_especiales("DÓLAR")
        'DOLAR'
        >>> limpiar_caracteres_especiales("NIÑO")
        'NINO'
        >>> limpiar_caracteres_especiales("Año 2025")
        'Ano 2025'
    """
    if not texto:
        return texto

    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_limpio = ''.join(
        char for char in texto_nfd
        if unicodedata.category(char) != 'Mn' # Mn = Mark, Nonspacing (acentos)
    )

    return texto_limpio

def normalizar_texto(
    texto: str,
    mantener_especiales: bool = True
) -> str:
    """
    Normaliza un texto según configuración.
    
    Args:
        texto: Texto a normalizar
        mantener_especiales: Si False, limpia caracteres especiales
        
    Returns:
        Texto normalizado
    """
    if mantener_especiales:
        return texto

    return limpiar_caracteres_especiales(texto)