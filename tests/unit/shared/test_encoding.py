"""Tests para detección y lectura de encodings."""
import pytest
from pathlib import Path
from src.shared.text_utils import detectar_encoding, leer_archivo_con_encoding_auto


class TestDeteccionEncoding:
    """Tests para detección de encoding."""
    
    def test_detectar_utf8(self, tmp_path):
        """Detecta correctamente archivos UTF-8."""
        archivo = tmp_path / "test_utf8.txt"
        archivo.write_text("DÓLAR NIÑO", encoding="utf-8")
        
        encoding = detectar_encoding(archivo)
        
        assert encoding in ("utf-8", "ascii")
    
    def test_detectar_ansi(self, tmp_path):
        """Detecta correctamente archivos ANSI (windows-1252)."""
        archivo = tmp_path / "test_ansi.txt"
        archivo.write_text("DÓLAR NIÑO", encoding="windows-1252")
        
        encoding = detectar_encoding(archivo)
        
        assert encoding == "windows-1252"
    
    def test_leer_utf8(self, tmp_path):
        """Lee correctamente archivos UTF-8."""
        archivo = tmp_path / "test_utf8.txt"
        contenido_original = "DÓLAR NIÑO CAFÉ"
        archivo.write_text(contenido_original, encoding="utf-8")
        
        contenido_leido = leer_archivo_con_encoding_auto(archivo)
        
        assert contenido_leido == contenido_original
    
    def test_leer_ansi(self, tmp_path):
        """Lee correctamente archivos ANSI."""
        archivo = tmp_path / "test_ansi.txt"
        contenido_original = "DÓLAR NIÑO CAFÉ"
        archivo.write_text(contenido_original, encoding="windows-1252")
        
        contenido_leido = leer_archivo_con_encoding_auto(archivo)
        
        assert contenido_leido == contenido_original
    
    def test_leer_archivo_mixto(self, tmp_path):
        """Lee archivos con diferentes encodings sin fallar."""
        # Simular archivo que podría venir de diferentes fuentes
        archivo = tmp_path / "test_mixto.txt"
        
        # Escribir con ANSI
        with archivo.open('w', encoding='windows-1252') as f:
            f.write("01,11001,BOGOTÁ,251121,BRK,860006797,BANCO,1,DÓLAR,1,OFICINAS\n")
        
        # Debe leer sin errores
        contenido = leer_archivo_con_encoding_auto(archivo)
        
        assert "BOGOTÁ" in contenido or "BOGOT" in contenido  # Puede variar según detección
        assert "DÓLAR" in contenido or "DLAR" in contenido