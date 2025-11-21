from __future__ import annotations
from dataclasses import dataclass

TIPO_VALOR_MAP = {
    1: "CU",   # Billete COP
    2: "CB",   # Moneda metálica COP
    3: "DA",   # Dólar americano
    4: "DC",   # Dólar canadiense
    5: "FF",
    6: "MA",
    7: "FS",
    8: "YJ",
    9: "LE",
    14: "CH",
    24: "EU",
    51: "SD",
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