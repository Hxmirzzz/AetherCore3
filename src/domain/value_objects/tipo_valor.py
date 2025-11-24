from __future__ import annotations
from dataclasses import dataclass

from src.domain.constants import CodigosDivisa as CD

TIPO_VALOR_MAP = {
    CD.CU: "CU",   # Billete COP
    CD.CB: "CB",   # Moneda metálica COP
    CD.DA: "DA",   # Dólar americano
    CD.DC: "DC",   # Dólar canadiense
    CD.FF: "FF",
    CD.MA: "MA",
    CD.FS: "FS",
    CD.YJ: "YJ",
    CD.LE: "LE",
    CD.CH: "CH",
    CD.EU: "EU",
    CD.SD: "SD",
}

@dataclass(frozen=True)
class TipoValor:
    codigo: int
    abreviatura: str

    @staticmethod
    def from_codigo(codigo: int) -> "TipoValor":
        abreviatura = TIPO_VALOR_MAP.get(codigo, "")
        return TipoValor(codigo=codigo, abreviatura=abreviatura)


# Validar denominaciones (AUN ESTA POR DEFINIR QUEDA GUARDADA COMO COMENTARIO)
#@dataclass(frozen=True)
#class TipoValor:
#    codigo: int
#    abreviatura: str
#    denominaciones_validas: tuple[int, ...] = field(default_factory=tuple)
#    
#
#@staticmethod
#def from_codigo(codigo: int) -> "TipoValor":
#    denominaciones_map = {
#        1: (100000, 50000, 20000, 10000, 5000, 2000, 1000, 500),  # CU
#        24: (500, 200, 100, 50, 20, 10, 5, 2),  # EU
#        # ... otros
#    }
#    
#    abreviatura = TIPO_VALOR_MAP.get(codigo, "")
#    denoms = denominaciones_map.get(codigo, ())
#    
#    return TipoValor(
#        codigo=codigo, 
#        abreviatura=abreviatura,
#        denominaciones_validas=denoms
#    )
#
#def validar_denominacion(self, valor: int) -> bool:
#    """Valida si una denominación es válida para este tipo de valor."""
#    if not self.denominaciones_validas:
#        return True  # Sin validación definida
#    return valor in self.denominaciones_validas