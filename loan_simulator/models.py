"""Modelos de datos del simulador de prestamos.

Este modulo no contiene logica de calculo ni logica de interfaz;
solo define las estructuras de datos que circulan entre ambas capas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List

# Metodos de amortizacion soportados
METHOD_FRENCH = "frances"   # cuota fija (sistema frances)
METHOD_GERMAN = "aleman"    # amortizacion fija (sistema aleman)

# Unidades de tiempo para el plazo
UNIT_MONTHS = "meses"
UNIT_YEARS = "anios"

METHOD_LABELS = {
    METHOD_FRENCH: "Frances (cuota fija)",
    METHOD_GERMAN: "Aleman (amortizacion fija)",
}

UNIT_LABELS = {
    UNIT_MONTHS: "Meses",
    UNIT_YEARS: "Anios",
}


@dataclass(frozen=True)
class LoanInput:
    """Datos de entrada del prestamo ya validados y normalizados."""

    principal: Decimal          # monto del prestamo
    annual_rate_percent: Decimal  # interes anual en porcentaje (ej: 12 = 12%)
    months: int                 # plazo convertido a meses
    method: str                 # METHOD_FRENCH | METHOD_GERMAN
    first_payment_date: date    # fecha de la primera cuota


@dataclass(frozen=True)
class PaymentRow:
    """Una fila de la tabla de amortizacion."""

    number: int          # numero de cuota (1..n)
    date: date           # fecha de pago
    payment: Decimal     # cuota (total a pagar)
    interest: Decimal    # componente de interes
    principal: Decimal   # componente de amortizacion (capital)
    balance: Decimal     # saldo restante despues del pago


@dataclass
class AmortizationResult:
    """Resultado completo de la simulacion."""

    rows: List[PaymentRow] = field(default_factory=list)
    total_paid: Decimal = Decimal("0.00")
    total_interest: Decimal = Decimal("0.00")
    monthly_payment: Decimal | None = None  # solo si la cuota es constante
