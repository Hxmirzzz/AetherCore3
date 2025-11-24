"""Tests para ExistenciasAggregatorService."""
import pytest
from datetime import date

from src.domain.entities.existencias import (
    ArchivoExistenciasOrigen,
    PlanoExistenciasHeader,
    PlanoExistenciasDetalle,
    DenominacionSaldo,
)
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.value_objects.tipo_valor import TipoValor


class TestExistenciasAggregatorService:
    """Tests para el servicio de agregación."""
    
    @pytest.fixture
    def archivo_bog_cu(self):
        """Archivo BOG tipo CU."""
        return ArchivoExistenciasOrigen(
            nombre_archivo="VYBUBOG2511210750CU.TXT",
            header=PlanoExistenciasHeader(
                tipo_registro="01",
                codigo_dane_ciudad="11001",
                nombre_ciudad="BOGOTA",
                fecha_certificado=FechaContable(value=date(2025, 11, 21)),
                codigo_transportadora="BRK",
                nit_cliente="860006797",
                nombre_cliente="BANCO",
                codigo_divisa=1,
                nombre_divisa="PESO",
                codigo_fondo=1,
                nombre_fondo="OFICINAS",
            ),
            detalles=[
                PlanoExistenciasDetalle(
                    tipo_registro="02",
                    tipo_valor=TipoValor.from_codigo(1),
                    nombre_tipo_valor="Peso",
                    codigo_calidad=2,
                    nombre_calidad="Buen Estado",
                    denominaciones=[DenominacionSaldo(100000, 5)],
                )
            ],
        )
    
    @pytest.fixture
    def archivo_ctg_cu(self):
        """Archivo CTG tipo CU."""
        return ArchivoExistenciasOrigen(
            nombre_archivo="VYBUCTG2511210752CU.TXT",
            header=PlanoExistenciasHeader(
                tipo_registro="01",
                codigo_dane_ciudad="13001",
                nombre_ciudad="CARTAGENA",
                fecha_certificado=FechaContable(value=date(2025, 11, 21)),
                codigo_transportadora="VAT",
                nit_cliente="860006797",
                nombre_cliente="BANCO",
                codigo_divisa=1,
                nombre_divisa="PESO",
                codigo_fondo=1,
                nombre_fondo="OFICINAS",
            ),
            detalles=[
                PlanoExistenciasDetalle(
                    tipo_registro="02",
                    tipo_valor=TipoValor.from_codigo(1),
                    nombre_tipo_valor="Peso",
                    codigo_calidad=2,
                    nombre_calidad="Buen Estado",
                    denominaciones=[DenominacionSaldo(50000, 10)],
                )
            ],
        )
    
    def test_construir_planos_nacionales_agrupa_por_tipo_valor(
        self, aggregator, archivo_bog_cu, archivo_ctg_cu
    ):
        """
        DADO: 2 archivos del mismo tipo de valor (CU)
        CUANDO: Construyo planos nacionales
        ENTONCES: Genera 1 plano nacional con 2 bloques
        """
        archivos = [archivo_bog_cu, archivo_ctg_cu]
        
        planos = aggregator.construir_planos_nacionales(archivos)
        
        assert len(planos) == 1
        plano = planos[0]
        assert plano.tipo_valor.codigo == 1
        assert len(plano.bloques) == 2
    
    def test_build_nacional_con_archivos_mismo_tipo_retorna_plano(
        self, aggregator, archivo_bog_cu, archivo_ctg_cu
    ):
        """
        DADO: 2 archivos con misma fecha y tipo de valor
        CUANDO: Construyo un nacional
        ENTONCES: Retorna un PlanoExistenciasNacional válido
        """
        archivos = [archivo_bog_cu, archivo_ctg_cu]
        
        plano = aggregator.build_nacional(archivos)
        
        assert plano.tipo_valor.codigo == 1
        assert plano.fecha_contable.value == date(2025, 11, 21)
        assert len(plano.bloques) == 2
    
    def test_build_nacional_sin_archivos_lanza_excepcion(self, aggregator):
        """
        DADO: Una lista vacía de archivos
        CUANDO: Intento construir un nacional
        ENTONCES: Lanza ValueError
        """
        with pytest.raises(ValueError, match="No se recibieron archivos"):
            aggregator.build_nacional([])