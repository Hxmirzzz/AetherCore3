"""Tests para las entidades del dominio de existencias."""
import pytest
from datetime import date

from src.domain.entities.existencias import (
    PlanoExistenciasHeader,
    PlanoExistenciasDetalle,
    DenominacionSaldo,
    ArchivoExistenciasOrigen,
    PlanoExistenciasNacional,
)
from src.domain.value_objects.fecha_contable import FechaContable
from src.domain.value_objects.tipo_valor import TipoValor


class TestDenominacionSaldo:
    """Tests para DenominacionSaldo."""
    
    def test_crear_denominacion_saldo_valida(self):
        """
        DADO: Un valor y cantidad válidos
        CUANDO: Creo una DenominacionSaldo
        ENTONCES: Se crea correctamente
        """
        denom = DenominacionSaldo(valor=100000, cantidad=5)
        
        assert denom.valor == 100000
        assert denom.cantidad == 5


class TestArchivoExistenciasOrigen:
    """Tests para ArchivoExistenciasOrigen."""
    
    @pytest.fixture
    def header_valido(self):
        """Header de prueba."""
        return PlanoExistenciasHeader(
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
        )
    
    @pytest.fixture
    def detalle_valido(self):
        """Detalle de prueba."""
        return PlanoExistenciasDetalle(
            tipo_registro="02",
            tipo_valor=TipoValor.from_codigo(1),
            nombre_tipo_valor="Peso",
            codigo_calidad=2,
            nombre_calidad="Buen Estado",
            denominaciones=[
                DenominacionSaldo(valor=100000, cantidad=5),
                DenominacionSaldo(valor=50000, cantidad=10),
            ],
        )
    
    def test_archivo_tiene_tipo_valor_del_primer_detalle(self, header_valido, detalle_valido):
        """
        DADO: Un archivo con detalles
        CUANDO: Accedo a su tipo_valor
        ENTONCES: Retorna el tipo_valor del primer detalle
        """
        archivo = ArchivoExistenciasOrigen(
            nombre_archivo="test.txt",
            header=header_valido,
            detalles=[detalle_valido],
        )
        
        assert archivo.tipo_valor.codigo == 1
        assert archivo.tipo_valor.abreviatura == "CU"
    
    def test_archivo_sin_detalles_usa_codigo_divisa_del_header(self, header_valido):
        """
        DADO: Un archivo sin detalles
        CUANDO: Accedo a su tipo_valor
        ENTONCES: Retorna el tipo_valor basado en codigo_divisa del header
        """
        archivo = ArchivoExistenciasOrigen(
            nombre_archivo="test.txt",
            header=header_valido,
            detalles=[],
        )
        
        assert archivo.tipo_valor.codigo == 1
    
    def test_archivo_con_multiples_tipos_valor_lanza_excepcion(self, header_valido):
        """
        DADO: Un archivo con detalles de diferentes tipos de valor
        CUANDO: Accedo a su tipo_valor
        ENTONCES: Lanza ValueError
        """
        detalle_cu = PlanoExistenciasDetalle(
            tipo_registro="02",
            tipo_valor=TipoValor.from_codigo(1),  # CU
            nombre_tipo_valor="Peso",
            codigo_calidad=2,
            nombre_calidad="Buen Estado",
            denominaciones=[],
        )
        
        detalle_eu = PlanoExistenciasDetalle(
            tipo_registro="02",
            tipo_valor=TipoValor.from_codigo(24),  # EU
            nombre_tipo_valor="Euro",
            codigo_calidad=2,
            nombre_calidad="Buen Estado",
            denominaciones=[],
        )
        
        archivo = ArchivoExistenciasOrigen(
            nombre_archivo="test.txt",
            header=header_valido,
            detalles=[detalle_cu, detalle_eu],
        )
        
        with pytest.raises(ValueError, match="múltiples tipos de valor"):
            _ = archivo.tipo_valor


class TestPlanoExistenciasNacional:
    """Tests para PlanoExistenciasNacional."""
    
    def test_to_lines_genera_formato_correcto(self):
        """
        DADO: Un plano nacional con un bloque
        CUANDO: Genero las líneas con to_lines()
        ENTONCES: Las líneas tienen el formato correcto
        """
        fecha = FechaContable(value=date(2025, 11, 21))
        tipo_valor = TipoValor.from_codigo(1)
        
        header = PlanoExistenciasHeader(
            tipo_registro="01",
            codigo_dane_ciudad="11001",
            nombre_ciudad="BOGOTA",
            fecha_certificado=fecha,
            codigo_transportadora="BRK",
            nit_cliente="860006797",
            nombre_cliente="BANCO",
            codigo_divisa=1,
            nombre_divisa="PESO",
            codigo_fondo=1,
            nombre_fondo="OFICINAS",
        )
        
        detalle = PlanoExistenciasDetalle(
            tipo_registro="02",
            tipo_valor=tipo_valor,
            nombre_tipo_valor="Peso",
            codigo_calidad=2,
            nombre_calidad="Buen Estado",
            denominaciones=[
                DenominacionSaldo(valor=100000, cantidad=5),
            ],
        )
        
        archivo = ArchivoExistenciasOrigen(
            nombre_archivo="test.txt",
            header=header,
            detalles=[detalle],
        )
        
        plano = PlanoExistenciasNacional(
            fecha_contable=fecha,
            tipo_valor=tipo_valor,
            bloques=[archivo],
        )
        
        lines = plano.to_lines()
        
        # Verificar que hay 2 líneas (1 header + 1 detalle)
        assert len(lines) == 2
        
        # Verificar header
        assert lines[0].startswith("01,")
        assert "BOGOTA" in lines[0]
        assert "21/11/2025" in lines[0]  # Fecha con barras
        
        # Verificar detalle
        assert lines[1].startswith("02,")
        assert "100000,5" in lines[1]