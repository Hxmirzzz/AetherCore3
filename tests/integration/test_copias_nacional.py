"""Tests para verificar el mecanismo de COPIAS de archivos nacionales."""
import pytest
from datetime import date, datetime
from pathlib import Path
import time

from src.application.orchestrators.existencias_orchestrator import ExistenciasOrchestratorOptions


class TestCopiasNacional:
    """Tests para el mecanismo de backups en COPIAS."""
    
    def test_archivo_nacional_existente_se_mueve_a_copias(
        self, orchestrator, archivo_origen_cu_valido, temp_dirs
    ):
        """
        DADO: Un archivo nacional ya existe
        CUANDO: Proceso un archivo del mismo tipo/fecha
        ENTONCES: El archivo anterior se mueve a COPIAS con timestamp
        """
        opts = ExistenciasOrchestratorOptions(fecha_contable=date(2025, 11, 21))
        
        # Primera ejecución: genera el nacional
        orchestrator.procesar_dia(opts)
        
        nacional_dir = temp_dirs["nacional"] / "251121"
        archivos_iniciales = list(nacional_dir.glob("VYBUBOG*CU.TXT"))
        assert len(archivos_iniciales) == 1
        
        nacional_original = archivos_iniciales[0]
        nombre_original = nacional_original.name
        
        # Esperar un poco para asegurar timestamp diferente
        time.sleep(0.1)
        
        # Crear otro archivo origen del mismo tipo/fecha (simula corrección)
        contenido_corregido = (
            "01,11001,BOGOTA,251121,BRK,860006797,BANCO,1,PESO,1,OFICINAS\n"
            "02,1,Peso,2,Buen Estado,200000,10,100000,5,50000,0,10000,0,5000,0,2000,0,1000,0,500,0\n"
        )
        archivo_correccion = temp_dirs["planos"] / "VYBUBOG2511210800CU.TXT"
        archivo_correccion.write_text(contenido_corregido, encoding="utf-8")
        
        # Segunda ejecución: procesa la corrección
        orchestrator.procesar_dia(opts)
        
        # Verificar que hay UN archivo nacional (el nuevo)
        archivos_finales = list(nacional_dir.glob("VYBUBOG*CU.TXT"))
        assert len(archivos_finales) == 1
        
        # Verificar que el archivo anterior se movió a COPIAS
        copias_dir = nacional_dir / "COPIAS"
        assert copias_dir.exists()
        
        archivos_copias = list(copias_dir.glob("VYBUBOG*CU*.TXT"))
        assert len(archivos_copias) >= 1
        
        # Verificar que el nombre tiene timestamp
        archivo_copia = archivos_copias[0]
        assert "_" in archivo_copia.name  # Debe tener formato: NOMBRE_timestamp.TXT
        assert archivo_copia.stem.startswith(nombre_original.replace(".TXT", ""))
    
    def test_multiples_correcciones_generan_multiples_copias(
        self, orchestrator, temp_dirs
    ):
        """
        DADO: Se procesan múltiples correcciones del mismo archivo
        CUANDO: Cada corrección reemplaza el nacional
        ENTONCES: Se generan múltiples copias en COPIAS/
        """
        fecha = date(2025, 11, 21)
        opts = ExistenciasOrchestratorOptions(fecha_contable=fecha)
        
        # Función helper para crear archivo de prueba
        def crear_archivo_cu(nombre: str, cantidad: int):
            contenido = (
                "01,11001,BOGOTA,251121,BRK,860006797,BANCO,1,PESO,1,OFICINAS\n"
                f"02,1,Peso,2,Buen Estado,100000,{cantidad},50000,0,20000,0,10000,0,5000,0,2000,0,1000,0,500,0\n"
            )
            archivo = temp_dirs["planos"] / nombre
            archivo.write_text(contenido, encoding="utf-8")
            return archivo
        
        # Crear 3 versiones del mismo archivo
        crear_archivo_cu("VYBUBOG2511210800CU.TXT", cantidad=1)
        orchestrator.procesar_dia(opts)
        time.sleep(0.1)
        
        # Limpiar PLANOS y crear segunda versión
        for f in temp_dirs["planos"].glob("*.TXT"):
            f.unlink()
        crear_archivo_cu("VYBUBOG2511210801CU.TXT", cantidad=2)
        orchestrator.procesar_dia(opts)
        time.sleep(0.1)
        
        # Limpiar PLANOS y crear tercera versión
        for f in temp_dirs["planos"].glob("*.TXT"):
            f.unlink()
        crear_archivo_cu("VYBUBOG2511210802CU.TXT", cantidad=3)
        orchestrator.procesar_dia(opts)
        
        # Verificar que hay UN archivo nacional actual
        nacional_dir = temp_dirs["nacional"] / "251121"
        archivos_nacionales = list(nacional_dir.glob("VYBUBOG*CU.TXT"))
        assert len(archivos_nacionales) == 1
        
        # Verificar que hay AL MENOS 2 copias (las versiones anteriores)
        copias_dir = nacional_dir / "COPIAS"
        archivos_copias = list(copias_dir.glob("VYBUBOG*CU*.TXT"))
        assert len(archivos_copias) >= 2
        
        # Verificar que todas las copias tienen timestamp diferente
        nombres_copias = [f.name for f in archivos_copias]
        assert len(nombres_copias) == len(set(nombres_copias))  # Todos únicos
    
    def test_copias_diferentes_tipos_valor_no_interfieren(
        self, orchestrator, archivo_origen_cu_valido, archivo_origen_eu_valido, temp_dirs
    ):
        """
        DADO: Archivos de diferentes tipos de valor (CU y EU)
        CUANDO: Se procesan múltiples veces
        ENTONCES: Las copias de CU y EU se manejan independientemente
        """
        opts = ExistenciasOrchestratorOptions(fecha_contable=date(2025, 11, 21))
        
        # Primera ejecución: genera CU y EU
        orchestrator.procesar_dia(opts)
        
        nacional_dir = temp_dirs["nacional"] / "251121"
        
        # Verificar que hay 2 nacionales (CU y EU)
        assert len(list(nacional_dir.glob("VYBUBOG*CU.TXT"))) == 1
        assert len(list(nacional_dir.glob("VYBUBOG*EU.TXT"))) == 1
        
        time.sleep(0.1)
        
        # Crear solo una corrección de CU (EU no se toca)
        # Primero limpiar PLANOS
        for f in temp_dirs["planos"].glob("*.TXT"):
            f.unlink()
        
        contenido_cu_corregido = (
            "01,11001,BOGOTA,251121,BRK,860006797,BANCO,1,PESO,1,OFICINAS\n"
            "02,1,Peso,2,Buen Estado,500000,1,100000,0,50000,0,10000,0,5000,0,2000,0,1000,0,500,0\n"
        )
        archivo_cu_correccion = temp_dirs["planos"] / "VYBUBOG2511210900CU.TXT"
        archivo_cu_correccion.write_text(contenido_cu_corregido, encoding="utf-8")
        
        # Segunda ejecución: procesa solo la corrección de CU
        orchestrator.procesar_dia(opts)
        
        # Verificar que solo CU tiene copia, EU no
        copias_dir = nacional_dir / "COPIAS"
        
        copias_cu = list(copias_dir.glob("VYBUBOG*CU*.TXT"))
        copias_eu = list(copias_dir.glob("VYBUBOG*EU*.TXT"))
        
        assert len(copias_cu) >= 1  # CU tiene al menos una copia
        assert len(copias_eu) == 0  # EU no tiene copias (no se reemplazó)