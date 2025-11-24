"""Tests de integración entre parser y reader."""
import pytest


class TestParserConReader:
    """Tests de integración parser + reader."""
    
    def test_parsear_archivo_desde_disco_funciona_correctamente(
        self, parser, archivo_origen_cu_valido
    ):
        """
        DADO: Un archivo físico en disco
        CUANDO: Lo parseo usando parser + reader
        ENTONCES: Se lee y parsea correctamente
        """
        resultado = parser.parse(archivo_origen_cu_valido)
        
        assert resultado is not None
        assert resultado.nombre_archivo == "VYBUBOG2511210750CU.TXT"
        assert resultado.header.nombre_ciudad == "BOGOTA"
        assert len(resultado.detalles) > 0