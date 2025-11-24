"""Tests para ExistenciasParserService."""
import pytest
from pathlib import Path
from datetime import date

from src.application.services.existencias_parser_service import ExistenciasParserService
from src.domain.entities.existencias import ArchivoExistenciasOrigen


class TestExistenciasParserService:
    """Tests para el servicio de parsing."""
    
    def test_parse_archivo_valido_retorna_archivo_origen(self, parser, archivo_origen_cu_valido):
        """
        DADO: Un archivo de existencias válido
        CUANDO: Lo parseo
        ENTONCES: Retorna ArchivoExistenciasOrigen con datos correctos
        """
        resultado = parser.parse(archivo_origen_cu_valido)
        
        assert isinstance(resultado, ArchivoExistenciasOrigen)
        assert resultado.nombre_archivo == "VYBUBOG2511210750CU.TXT"
        assert resultado.header.nombre_ciudad == "BOGOTA"
        assert len(resultado.detalles) == 1
    
    def test_parse_archivo_vacio_lanza_excepcion(self, parser, temp_dirs):
        """
        DADO: Un archivo vacío
        CUANDO: Intento parsearlo
        ENTONCES: Lanza ValueError
        """
        archivo_vacio = temp_dirs["planos"] / "vacio.txt"
        archivo_vacio.write_text("", encoding="utf-8")
        
        with pytest.raises(ValueError, match="vacio"):
            parser.parse(archivo_vacio)
    
    def test_parse_archivo_sin_header_lanza_excepcion(self, parser, temp_dirs):
        """
        DADO: Un archivo sin registro 01
        CUANDO: Intento parsearlo
        ENTONCES: Lanza ValueError
        """
        contenido = "02,1,Peso,2,Buen Estado,100000,5\n"
        archivo = temp_dirs["planos"] / "sin_header.txt"
        archivo.write_text(contenido, encoding="utf-8")
        
        with pytest.raises(ValueError):
            parser.parse(archivo)
    
    def test_parse_archivo_sin_detalles_lanza_excepcion(self, parser, temp_dirs):
        """
        DADO: Un archivo solo con header (sin detalles)
        CUANDO: Intento parsearlo
        ENTONCES: Lanza ValueError
        """
        contenido = "01,11001,BOGOTA,251121,BRK,860006797,BANCO,1,PESO,1,OFICINAS\n"
        archivo = temp_dirs["planos"] / "sin_detalles.txt"
        archivo.write_text(contenido, encoding="utf-8")
        
        with pytest.raises(ValueError, match="sin registros 02"):
            parser.parse(archivo)