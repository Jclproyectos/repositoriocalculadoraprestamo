"""Tabla (Treeview) que muestra la amortizacion cuota a cuota."""

from __future__ import annotations

from tkinter import ttk

from ..models import AmortizationResult

COLUMNS = ("numero", "fecha", "cuota", "interes", "amortizacion", "saldo")

HEADINGS = {
    "numero": "#",
    "fecha": "Fecha",
    "cuota": "Cuota a pagar",
    "interes": "Interes",
    "amortizacion": "Amortizacion",
    "saldo": "Saldo",
}

WIDTHS = {
    "numero": 50,
    "fecha": 100,
    "cuota": 130,
    "interes": 120,
    "amortizacion": 130,
    "saldo": 130,
}


def _money(value) -> str:
    return f"{value:,.2f}"


class ScheduleTable(ttk.Frame):
    """Widget reutilizable con la tabla de amortizacion y sus barras de scroll."""

    def __init__(self, master):
        super().__init__(master)
        self.tree = ttk.Treeview(
            self, columns=COLUMNS, show="headings", selectmode="none"
        )

        for column in COLUMNS:
            anchor = "center" if column in ("numero", "fecha") else "e"
            self.tree.heading(column, text=HEADINGS[column], anchor=anchor)
            self.tree.column(column, width=WIDTHS[column], anchor=anchor, stretch=True)

        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd", background="#f8fafc")
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("total", background="#e2e8f0", font=("Segoe UI", 9, "bold"))

    def render(self, result: AmortizationResult, total_principal) -> None:
        self.clear()
        for row in result.rows:
            tags = ("odd",) if row.number % 2 else ("even",)
            self.tree.insert(
                "", "end", tags=tags,
                values=(
                    row.number,
                    row.date.strftime("%d/%m/%Y"),
                    _money(row.payment),
                    _money(row.interest),
                    _money(row.principal),
                    _money(row.balance),
                ),
            )
        self.tree.insert(
            "", "end", tags=("total",),
            values=(
                "", "TOTALES",
                _money(result.total_paid),
                _money(result.total_interest),
                _money(total_principal),
                "0.00",
            ),
        )

    def clear(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
