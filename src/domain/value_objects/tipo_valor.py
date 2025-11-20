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