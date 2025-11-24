"""
Fixtures compartidos para todos los tests.
"""
import pytest
from pathlib import Path
from datetime import date

from src.infrastructure.file_system.existencias_path_manager import ExistenciasPathManager
from src.infrastructure.file_system.existencias_txt_reader import ExistenciasTxtReader
from src.infrastructure.file_system.existencias_txt_writer import ExistenciasTxtWriter
from src.application.services.existencias_parser_service import ExistenciasParserService
from src.application.services.existencias_aggregator_service import ExistenciasAggregatorService
from src.application.services.existencias_output_service import ExistenciasOutputService
from src.application.orchestrators.existencias_orchestrator import ExistenciasProcessingOrchestrator


@pytest.fixture
def temp_dirs(tmp_path):
    """
    Crea estructura de directorios temporales para tests.
    
    Returns:
        dict con paths: planos, nacional, gestionados, errores
    """
    planos_dir = tmp_path / "PLANOS"
    planos_dir.mkdir()
    
    nacional_dir = tmp_path / "NACIONAL"
    nacional_dir.mkdir()
    
    gestionados_dir = planos_dir / "GESTIONADOS"
    gestionados_dir.mkdir()
    
    errores_dir = planos_dir / "ERRORES"
    errores_dir.mkdir()
    
    return {
        "planos": planos_dir,
        "nacional": nacional_dir,
        "gestionados": gestionados_dir,
        "errores": errores_dir,
    }


@pytest.fixture
def path_manager(temp_dirs):
    """Path manager con directorios temporales."""
    return ExistenciasPathManager(
        origen_planos=temp_dirs["planos"],
        origen_nacional=temp_dirs["nacional"],
    )


@pytest.fixture
def reader(path_manager):
    """Reader configurado con path manager temporal."""
    return ExistenciasTxtReader(path_manager)


@pytest.fixture
def writer(path_manager):
    """Writer configurado con path manager temporal."""
    return ExistenciasTxtWriter(path_manager)


@pytest.fixture
def parser(reader):
    """Parser service configurado."""
    return ExistenciasParserService(reader)


@pytest.fixture
def aggregator():
    """Aggregator service."""
    return ExistenciasAggregatorService()


@pytest.fixture
def output_service(writer):
    """Output service configurado."""
    return ExistenciasOutputService(writer)


@pytest.fixture
def orchestrator(parser, aggregator, output_service, reader, path_manager):
    """Orchestrator completo configurado."""
    return ExistenciasProcessingOrchestrator(
        parser=parser,
        aggregator=aggregator,
        output=output_service,
        reader=reader,
        path_manager=path_manager,
    )


@pytest.fixture
def archivo_origen_cu_valido(temp_dirs):
    """
    Crea un archivo origen válido de tipo CU (pesos).
    
    Returns:
        Path del archivo creado
    """
    contenido = (
        "01,11001,BOGOTA,251121,BRK,860006797,BANCO,1,PESO,1,OFICINAS\n"
        "02,1,Peso,2,Buen Estado,100000,5,50000,10,20000,0,10000,2,5000,0,2000,0,1000,0,500,0\n"
    )
    
    archivo = temp_dirs["planos"] / "VYBUBOG2511210750CU.TXT"
    archivo.write_text(contenido, encoding="utf-8")
    
    return archivo


@pytest.fixture
def archivo_origen_eu_valido(temp_dirs):
    """
    Crea un archivo origen válido de tipo EU (euros).
    
    Returns:
        Path del archivo creado
    """
    contenido = (
        "01,13001,CARTAGENA,251121,VAT,860006797,BANCO,24,EURO,1,OFICINAS\n"
        "02,24,Euro,2,Buen Estado,500,0,200,5,100,0,50,10,20,0,10,0,5,0,2,0\n"
    )
    
    archivo = temp_dirs["planos"] / "VYBUCTG2511210752EU.TXT"
    archivo.write_text(contenido, encoding="utf-8")
    
    return archivo


@pytest.fixture
def fecha_prueba():
    """Fecha fija para tests."""
    return date(2025, 11, 21)