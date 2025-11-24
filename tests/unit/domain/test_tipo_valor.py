"""Tests para el value object TipoValor."""
import pytest
from src.domain.value_objects.tipo_valor import TipoValor


class TestTipoValor:
    """Tests para TipoValor."""
    
    def test_from_codigo_cu_retorna_codigo_y_abreviatura_correctos(self):
        """
        DADO: El código 1 (peso colombiano)
        CUANDO: Creo un TipoValor
        ENTONCES: Tiene código 1 y abreviatura "CU"
        """
        tipo_valor = TipoValor.from_codigo(1)
        
        assert tipo_valor.codigo == 1
        assert tipo_valor.abreviatura == "CU"
    
    def test_from_codigo_eu_retorna_codigo_y_abreviatura_correctos(self):
        """
        DADO: El código 24 (euro)
        CUANDO: Creo un TipoValor
        ENTONCES: Tiene código 24 y abreviatura "EU"
        """
        tipo_valor = TipoValor.from_codigo(24)
        
        assert tipo_valor.codigo == 24
        assert tipo_valor.abreviatura == "EU"
    
    def test_from_codigo_da_retorna_codigo_y_abreviatura_correctos(self):
        """
        DADO: El código 3 (dólar americano)
        CUANDO: Creo un TipoValor
        ENTONCES: Tiene código 3 y abreviatura "DA"
        """
        tipo_valor = TipoValor.from_codigo(3)
        
        assert tipo_valor.codigo == 3
        assert tipo_valor.abreviatura == "DA"
    
    def test_from_codigo_desconocido_retorna_abreviatura_vacia(self):
        """
        DADO: Un código no mapeado (999)
        CUANDO: Creo un TipoValor
        ENTONCES: Tiene código 999 y abreviatura vacía
        """
        tipo_valor = TipoValor.from_codigo(999)
        
        assert tipo_valor.codigo == 999
        assert tipo_valor.abreviatura == ""
    
    def test_tipo_valor_es_inmutable(self):
        """
        DADO: Un TipoValor creado
        CUANDO: Intento modificar sus atributos
        ENTONCES: Lanza FrozenInstanceError
        """
        tipo_valor = TipoValor.from_codigo(1)
        
        with pytest.raises(Exception):  # dataclass frozen
            tipo_valor.codigo = 2
    
    def test_tipos_valor_con_mismo_codigo_son_iguales(self):
        """
        DADO: Dos TipoValor con el mismo código
        CUANDO: Los comparo
        ENTONCES: Son iguales
        """
        tipo1 = TipoValor.from_codigo(1)
        tipo2 = TipoValor.from_codigo(1)
        
        assert tipo1 == tipo2
    
    def test_tipos_valor_con_diferente_codigo_son_diferentes(self):
        """
        DADO: Dos TipoValor con diferentes códigos
        CUANDO: Los comparo
        ENTONCES: Son diferentes
        """
        tipo1 = TipoValor.from_codigo(1)
        tipo2 = TipoValor.from_codigo(24)
        
        assert tipo1 != tipo2