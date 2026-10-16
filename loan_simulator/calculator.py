"""Motor de calculo de la tabla de amortizacion.

Modulo puro: no depende de la interfaz grafica ni de archivos,
solo de los modelos y de decimal (precision exacta en dinero).
"""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    METHOD_FRENCH,
    METHOD_GERMAN,
    AmortizationResult,
    LoanInput,
    PaymentRow,
)

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """Redondea un importe monetario a 2 decimales (banco)."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def add_months(base: date, months: int) -> date:
    """Suma meses a una fecha sin desbordar el dia del mes."""
    total = base.month - 1 + months
    year = base.year + total // 12
    month = total % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def monthly_rate(loan: LoanInput) -> Decimal:
    """Tasa de interes mensual equivalente a la tasa anual informada."""
    return loan.annual_rate_percent / Decimal(100) / Decimal(12)


def calculate(loan: LoanInput) -> AmortizationResult:
    """Genera la tabla de amortizacion completa."""
    if loan.method == METHOD_FRENCH:
        return _french_schedule(loan)
    if loan.method == METHOD_GERMAN:
        return _german_schedule(loan)
    raise ValueError(f"Metodo de amortizacion no soportado: {loan.method}")


def _french_schedule(loan: LoanInput) -> AmortizationResult:
    """Sistema frances: cuota constante, al inicio carga mas interes."""
    principal = loan.principal
    rate = monthly_rate(loan)
    months = loan.months

    if rate == 0:
        payment = money(principal / months)
    else:
        factor = (1 + rate) ** months
        payment = money(principal * rate * factor / (factor - 1))

    balance = principal
    rows: list[PaymentRow] = []

    for i in range(1, months + 1):
        interest = money(balance * rate)
        principal_part = payment - interest

        # Ultima cuota (o ajuste por redondeos): se amortiza todo el saldo.
        if i == months or principal_part > balance:
            principal_part = balance
            payment_i = money(principal_part + interest)
        else:
            payment_i = payment

        balance = money(balance - principal_part)
        if balance < 0:
            balance = Decimal("0.00")

        rows.append(
            PaymentRow(
                number=i,
                date=add_months(loan.first_payment_date, i - 1),
                payment=payment_i,
                interest=interest,
                principal=money(principal_part),
                balance=balance,
            )
        )

    return _build_result(rows, monthly_payment=payment)


def _german_schedule(loan: LoanInput) -> AmortizationResult:
    """Sistema aleman: amortizacion de capital constante, cuota decreciente."""
    principal = loan.principal
    rate = monthly_rate(loan)
    months = loan.months
    base_amortization = money(principal / months)

    balance = principal
    rows: list[PaymentRow] = []

    for i in range(1, months + 1):
        interest = money(balance * rate)

        if i == months:
            principal_part = balance  # absorbe los decimales del redondeo
        else:
            principal_part = base_amortization

        payment_i = money(principal_part + interest)

        balance = money(balance - principal_part)
        if balance < 0:
            balance = Decimal("0.00")

        rows.append(
            PaymentRow(
                number=i,
                date=add_months(loan.first_payment_date, i - 1),
                payment=payment_i,
                interest=interest,
                principal=money(principal_part),
                balance=balance,
            )
        )

    return _build_result(rows, monthly_payment=None)


def _build_result(
    rows: list[PaymentRow], monthly_payment: Decimal | None
) -> AmortizationResult:
    total_paid = sum((row.payment for row in rows), Decimal("0.00"))
    total_interest = sum((row.interest for row in rows), Decimal("0.00"))
    return AmortizationResult(
        rows=rows,
        total_paid=total_paid,
        total_interest=total_interest,
        monthly_payment=monthly_payment,
    )
