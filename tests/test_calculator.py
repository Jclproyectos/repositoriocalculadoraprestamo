"""Pruebas unitarias del motor de calculo (sin interfaz grafica).

Ejecutar con:  python -m unittest discover -s tests -v
"""

import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loan_simulator.calculator import calculate, add_months
from loan_simulator.models import METHOD_FRENCH, METHOD_GERMAN, LoanInput
from loan_simulator.validators import LoanValidationError, build_loan


def make_loan(method=METHOD_FRENCH, principal="10000", rate="12", months=12):
    return LoanInput(
        principal=Decimal(principal),
        annual_rate_percent=Decimal(rate),
        months=months,
        method=method,
        first_payment_date=date(2026, 1, 15),
    )


class CalculatorTests(unittest.TestCase):
    def test_french_final_balance_is_zero(self):
        result = calculate(make_loan(METHOD_FRENCH))
        self.assertEqual(result.rows[-1].balance, Decimal("0.00"))
        self.assertEqual(len(result.rows), 12)

    def test_french_totals_are_consistent(self):
        result = calculate(make_loan(METHOD_FRENCH))
        capital = sum((r.principal for r in result.rows), Decimal("0"))
        self.assertEqual(capital, Decimal("10000.00"))
        self.assertEqual(result.total_paid, result.total_interest + Decimal("10000.00"))
        # Cuota fija en todas las filas salvo la ultima (ajuste de redondeo)
        first = result.rows[0].payment
        self.assertEqual(result.monthly_payment, first)
        for row in result.rows[:-1]:
            self.assertEqual(row.payment, first)

    def test_zero_interest_is_allowed(self):
        result = calculate(make_loan(METHOD_FRENCH, rate="0", months=10))
        self.assertEqual(result.total_interest, Decimal("0.00"))
        self.assertEqual(result.rows[-1].balance, Decimal("0.00"))
        for row in result.rows:
            self.assertEqual(row.interest, Decimal("0.00"))

    def test_german_has_constant_amortization(self):
        result = calculate(make_loan(METHOD_GERMAN, principal="12000", months=12))
        amortizations = [r.principal for r in result.rows[:-1]]
        self.assertTrue(all(a == Decimal("1000.00") for a in amortizations))
        self.assertEqual(result.rows[-1].balance, Decimal("0.00"))
        # Cuotas decrecientes en sistema aleman
        self.assertGreater(result.rows[0].payment, result.rows[-1].payment)

    def test_dates_advance_monthly(self):
        result = calculate(make_loan(months=3))
        self.assertEqual(result.rows[0].date, date(2026, 1, 15))
        self.assertEqual(result.rows[1].date, date(2026, 2, 15))
        self.assertEqual(result.rows[2].date, date(2026, 3, 15))

    def test_add_months_handles_end_of_month(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2026, 12, 15), 1), date(2027, 1, 15))


class ValidatorTests(unittest.TestCase):
    def test_valid_input(self):
        loan = build_loan("15000", "10,5", "2", "anios",
                          METHOD_FRENCH, date(2026, 2, 1))
        self.assertEqual(loan.months, 24)
        self.assertEqual(loan.principal, Decimal("15000"))

    def test_negative_principal_rejected(self):
        with self.assertRaises(LoanValidationError):
            build_loan("-500", "10", "12", "meses", METHOD_FRENCH, date(2026, 2, 1))

    def test_non_numeric_term_rejected(self):
        with self.assertRaises(LoanValidationError):
            build_loan("1000", "10", "doce", "meses", METHOD_FRENCH, date(2026, 2, 1))

    def test_missing_date_rejected(self):
        with self.assertRaises(LoanValidationError):
            build_loan("1000", "10", "12", "meses", METHOD_FRENCH, None)

    def test_date_format_validated_in_ui_helper(self):
        from loan_simulator.ui.input_panel import parse_date

        self.assertEqual(parse_date("15/03/2026"), date(2026, 3, 15))
        with self.assertRaises(LoanValidationError):
            parse_date("2026-03-15")


if __name__ == "__main__":
    unittest.main()
