"""Exportacion de la tabla de amortizacion a archivos (CSV / TXT)."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import METHOD_LABELS, AmortizationResult, LoanInput

CSV_SEPARATOR = ";"
HEADER_ENCODING = "utf-8-sig"  # acentos correctos al abrir en Excel


def export_schedule(path, loan: LoanInput, result: AmortizationResult) -> Path:
    """Guarda la simulacion completa en un archivo CSV delimitado con ';'."""
    target = Path(path)
    method_name = METHOD_LABELS.get(loan.method, loan.method)

    with target.open("w", newline="", encoding=HEADER_ENCODING) as handle:
        writer = csv.writer(handle, delimiter=CSV_SEPARATOR)
        writer.writerow(["Simulador de Prestamos - Tabla de amortizacion"])
        writer.writerow(["Prestamo", format(loan.principal, ".2f")])
        writer.writerow(["Interes anual (%)", format(loan.annual_rate_percent, ".2f")])
        writer.writerow(["Plazo (meses)", loan.months])
        writer.writerow(["Metodo", method_name])
        writer.writerow(["Primera cuota", loan.first_payment_date.strftime("%d/%m/%Y")])
        writer.writerow([])
        writer.writerow(["Cuota", "Fecha", "Cuota a pagar", "Interes", "Amortizacion", "Saldo"])
        for row in result.rows:
            writer.writerow(
                [
                    row.number,
                    row.date.strftime("%d/%m/%Y"),
                    format(row.payment, ".2f"),
                    format(row.interest, ".2f"),
                    format(row.principal, ".2f"),
                    format(row.balance, ".2f"),
                ]
            )
        writer.writerow([])
        writer.writerow(["", "TOTALES", format(result.total_paid, ".2f"),
                         format(result.total_interest, ".2f"),
                         format(loan.principal, ".2f"), "0.00"])
    return target
