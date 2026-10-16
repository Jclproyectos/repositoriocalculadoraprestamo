"""Validacion y conversion de los datos que ingresa el usuario.

Convierte texto crudo (de los campos de la interfaz) en un objeto
:class:`LoanInput` listo para el motor de calculo.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from .models import (
    METHOD_FRENCH,
    METHOD_GERMAN,
    UNIT_MONTHS,
    UNIT_YEARS,
    LoanInput,
)

MAX_MONTHS = 1200  # 100 anios: proteccion contra datos absurdos


class LoanValidationError(ValueError):
    """Error de negocio provocado por datos invalidos del usuario."""


def parse_decimal(text, field_name: str) -> Decimal:
    """Convierte un texto en Decimal aceptando coma o punto decimal."""
    if text is None:
        raise LoanValidationError(f"El campo '{field_name}' es obligatorio.")
    cleaned = str(text).strip().replace(" ", "").replace(",", ".")
    if not cleaned:
        raise LoanValidationError(f"El campo '{field_name}' es obligatorio.")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise LoanValidationError(
            f"El campo '{field_name}' debe ser un numero valido (ej: 15000 o 12.5)."
        )
    return value


def parse_int(text, field_name: str) -> int:
    if text is None:
        raise LoanValidationError(f"El campo '{field_name}' es obligatorio.")
    cleaned = str(text).strip()
    if not cleaned:
        raise LoanValidationError(f"El campo '{field_name}' es obligatorio.")
    try:
        return int(cleaned)
    except ValueError:
        raise LoanValidationError(f"El campo '{field_name}' debe ser un numero entero.")


def build_loan(
    principal_text,
    rate_text,
    term_text,
    unit: str,
    method: str,
    first_payment_date: date,
) -> LoanInput:
    """Valida los datos crudos de la interfaz y construye el LoanInput."""

    principal = parse_decimal(principal_text, "Prestamo")
    if principal <= 0:
        raise LoanValidationError("El monto del prestamo debe ser mayor que 0.")

    rate = parse_decimal(rate_text, "Interes")
    if rate < 0:
        raise LoanValidationError("La tasa de interes no puede ser negativa.")
    if rate > 1000:
        raise LoanValidationError("La tasa de interes parece demasiado alta (max: 1000%).")

    term = parse_int(term_text, "Tiempo")
    if term <= 0:
        raise LoanValidationError("El plazo debe ser mayor que 0.")

    if unit == UNIT_YEARS:
        months = term * 12
    elif unit == UNIT_MONTHS:
        months = term
    else:
        raise LoanValidationError("Debe seleccionar una unidad de tiempo valida.")

    if months > MAX_MONTHS:
        raise LoanValidationError(
            f"El plazo supera el maximo permitido ({MAX_MONTHS} meses)."
        )

    if method not in (METHOD_FRENCH, METHOD_GERMAN):
        raise LoanValidationError("Debe seleccionar un metodo de amortizacion valido.")

    if first_payment_date is None:
        raise LoanValidationError("Debe indicar la fecha de la primera cuota.")

    return LoanInput(
        principal=principal,
        annual_rate_percent=rate,
        months=months,
        method=method,
        first_payment_date=first_payment_date,
    )
