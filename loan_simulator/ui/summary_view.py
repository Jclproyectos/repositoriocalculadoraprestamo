"""Resumen general de la simulacion (totales y cuota)."""

from __future__ import annotations

from tkinter import StringVar, ttk

from ..models import METHOD_FRENCH, AmortizationResult, LoanInput


class SummaryView(ttk.Frame):
    """Muestra los indicadores globales calculados."""

    def __init__(self, master):
        super().__init__(master, padding=(16, 10))

        self.payment_label = StringVar(value="Cuota: -")
        self.paid_label = StringVar(value="Total a pagar: -")
        self.interest_label = StringVar(value="Total intereses: -")
        self.count_label = StringVar(value="Cuotas: -")
        self.ratio_label = StringVar(value="Interes / prestamo: -")

        style_font = ("Segoe UI", 11, "bold")
        for column, variable in enumerate(
            (self.payment_label, self.paid_label, self.interest_label,
             self.count_label, self.ratio_label)
        ):
            label = ttk.Label(self, textvariable=variable, font=style_font, anchor="w")
            label.grid(row=0, column=column, sticky="w", padx=(0, 26), pady=(4, 4))
            self.columnconfigure(column, weight=1)

    def render(self, loan: LoanInput, result: AmortizationResult) -> None:
        if result.monthly_payment is not None:
            self.payment_label.set(f"Cuota fija: {result.monthly_payment:,.2f}")
        else:
            first = result.rows[0].payment if result.rows else 0
            self.payment_label.set(f"1ra cuota: {first:,.2f}")

        self.paid_label.set(f"Total a pagar: {result.total_paid:,.2f}")
        self.interest_label.set(f"Total intereses: {result.total_interest:,.2f}")
        self.count_label.set(f"Cuotas: {len(result.rows)}")

        if loan.principal > 0:
            ratio = (result.total_interest / loan.principal) * 100
            self.ratio_label.set(f"Interes / prestamo: {ratio:,.1f}%")

    def clear(self) -> None:
        for variable in (
            self.payment_label, self.paid_label, self.interest_label,
            self.count_label, self.ratio_label,
        ):
            variable.set(variable.get().split(":")[0] + ": -")
