"""
Utilidades para manipulación de texto.
"""
import unicodedata

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