"""Tests para utilidades de texto."""
import pytest
from src.shared.text_utils import limpiar_caracteres_especiales, normalizar_texto


class TestLimpiarCaracteresEspeciales:
    """Tests para limpieza de caracteres especiales."""
    
    def test_limpiar_vocales_acentuadas(self):
        """Limpia vocales acentuadas correctamente."""
        assert limpiar_caracteres_especiales("DÓLAR") == "DOLAR"
        assert limpiar_caracteres_especiales("CAFÉ") == "CAFE"
        assert limpiar_caracteres_especiales("LEÓN") == "LEON"
    
    def test_limpiar_enie(self):
        """Limpia ñ correctamente."""
        assert limpiar_caracteres_especiales("NIÑO") == "NINO"
        assert limpiar_caracteres_especiales("AÑO") == "ANO"
        assert limpiar_caracteres_especiales("España") == "Espana"
    
    def test_mantener_espacios_y_numeros(self):
        """Mantiene espacios y números."""
        assert limpiar_caracteres_especiales("Año 2025") == "Ano 2025"
        assert limpiar_caracteres_especiales("100 DÓLARES") == "100 DOLARES"
    
    def test_texto_vacio(self):
        """Maneja texto vacío."""
        assert limpiar_caracteres_especiales("") == ""
        assert limpiar_caracteres_especiales(None) == None
    
    def test_texto_sin_especiales(self):
        """No modifica texto sin caracteres especiales."""
        assert limpiar_caracteres_especiales("DOLLAR") == "DOLLAR"
        assert limpiar_caracteres_especiales("USD") == "USD"


class TestNormalizarTexto:
    """Tests para normalización de texto."""
    
    def test_mantener_especiales_true(self):
        """Con mantener_especiales=True, no cambia nada."""
        texto = "DÓLAR NIÑO"
        assert normalizar_texto(texto, mantener_especiales=True) == texto
    
    def test_mantener_especiales_false(self):
        """Con mantener_especiales=False, limpia caracteres."""
        assert normalizar_texto("DÓLAR", mantener_especiales=False) == "DOLAR"
        assert normalizar_texto("NIÑO", mantener_especiales=False) == "NINO"