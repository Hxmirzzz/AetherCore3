"""Tests de integración del orchestrator."""
import pytest
from datetime import date

from src.application.orchestrators.existencias_orchestrator import ExistenciasOrchestratorOptions


class TestOrchestrator:
    """Tests de integración del orchestrator."""
    
    def test_procesar_dia_con_archivos_validos_genera_nacionales(
        self, orchestrator, archivo_origen_cu_valido, archivo_origen_eu_valido, temp_dirs
    ):
        """
        DADO: 2 archivos válidos (CU y EU) en PLANOS
        CUANDO: Ejecuto procesar_dia()
        ENTONCES: Se generan 2 archivos nacionales
        """
        opts = ExistenciasOrchestratorOptions(fecha_contable=date(2025, 11, 21))
        
        orchestrator.procesar_dia(opts)
        
        # Verificar que se generaron archivos nacionales
        nacional_dir = temp_dirs["nacional"] / "251121"
        assert nacional_dir.exists()
        
        archivos_nacionales = list(nacional_dir.glob("VYBUBOG*.TXT"))
        assert len(archivos_nacionales) == 2  # CU y EU
    
    def test_procesar_dia_mueve_archivos_a_gestionados(
        self, orchestrator, archivo_origen_cu_valido, temp_dirs
    ):
        """
        DADO: 1 archivo válido en PLANOS
        CUANDO: Ejecuto procesar_dia()
        ENTONCES: El archivo se mueve a GESTIONADOS
        """
        opts = ExistenciasOrchestratorOptions(fecha_contable=date(2025, 11, 21))
        
        orchestrator.procesar_dia(opts)
        
        # Verificar que se movió a gestionados
        gestionados = temp_dirs["gestionados"]
        archivos_gestionados = list(gestionados.glob("*.TXT"))
        assert len(archivos_gestionados) == 1
        assert archivos_gestionados[0].name == "VYBUBOG2511210750CU.TXT"