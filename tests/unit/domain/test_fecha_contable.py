from multiprocessing import Value
import pytest
from datetime import date
from src.domain.value_objects.fecha_contable import FechaContable

class TestFechaContable:
    """
    Tests para el value object FechaContable.
    Cada test verifica UNA cosa específica.
    """

    def test_from_yymmdd_formato_valido(self):
        """
        DADO: Una fecha en formato yymmdd válido
        CUANDO: La parseo con from_yymmdd
        ENTONCES: Obtengo el date correcto
        """

        fecha_str = "251122"
        resultado = FechaContable.from_yymmdd(fecha_str)
        assert resultado.value == date(2025, 11, 22)

    def test_from_yymmdd_formato_valido_lanza_exception(self):
        """
        DADO: Una fecha con formato inválido
        CUANDO: Intento parsearla
        ENTONCES: Lanza ValueError
        """
        with pytest.raises(ValueError):
            FechaContable.from_yymmdd("INVALIDO")

    def test_to_ddmmyyyy_retorna_formato_con_barras(self):
        """
        DADO: Una FechaContable
        CUANDO: La convierto a string con to_ddmmyyyy
        ENTONCES: Obtengo formato dd/mm/yyyy con barras
        """
        fecha = FechaContable(value=date(2025, 11, 22))
        resultado = fecha.to_ddmmyyyy()
        assert resultado == "22/11/2025"
        assert "/" in resultado

    def test_from_filename_extrae_fecha_correctamente(self):
        """
        DADO: Un nombre de archivo válido
        CUANDO: Extraigo la fecha con from_filename
        ENTONCES: Obtengo la fecha correcta
        """
        nombre = "VYBUBOG2511220750CU.TXT"
        resultado = FechaContable.from_filename(nombre)
        assert resultado.value == date(2025, 11, 22)

    def test_from_filename_con_nombre_invalido_lanza_excepcion(self):
        """
        DADO: Un nombre de archivo sin fecha válida
        CUANDO: Intento extraer fecha
        ENTONCES: Lanza excepción
        """
        with pytest.raises(Exception):
            FechaContable.from_filename("ARCHIVO_SIN_FECHA.TXT")