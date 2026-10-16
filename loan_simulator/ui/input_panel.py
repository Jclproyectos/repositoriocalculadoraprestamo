"""Panel de entrada de datos (formulario del usuario)."""

from __future__ import annotations

from datetime import date, datetime
from tkinter import StringVar, ttk

from ..models import METHOD_FRENCH, METHOD_GERMAN, UNIT_MONTHS, UNIT_YEARS
from ..validators import LoanValidationError

METHOD_CHOICES = ["Frances (cuota fija)", "Aleman (amortizacion fija)"]
UNIT_CHOICES = ["Meses", "Anios"]

_LABELS_FONT = ("Segoe UI", 9)
_ENTRY_FONT = ("Segoe UI", 10)


def parse_date(text: str) -> date:
    """Convierte 'dd/mm/aaaa' a date, con mensaje amigable si es invalida."""
    cleaned = (text or "").strip()
    try:
        return datetime.strptime(cleaned, "%d/%m/%Y").date()
    except ValueError:
        raise LoanValidationError(
            "La fecha de la primera cuota debe tener el formato dd/mm/aaaa."
        )


class InputPanel(ttk.Frame):
    """Formulario con prestamo, interes, tiempo y opciones de simulacion."""

    def __init__(self, master, on_calculate, on_clear, on_export):
        super().__init__(master, padding=(16, 12))
        self.on_calculate = on_calculate
        self.on_clear = on_clear
        self.on_export = on_export

        self.principal_var = StringVar(value="10000")
        self.rate_var = StringVar(value="12")
        self.term_var = StringVar(value="24")
        self.unit_var = StringVar(value="Meses")
        self.method_var = StringVar(value="Frances (cuota fija)")
        self.date_var = StringVar(value=date.today().strftime("%d/%m/%Y"))

        self._build()

    # ------------------------------------------------------------------ UI
    def _build(self) -> None:
        title = ttk.Label(
            self, text="Simulador de Prestamos",
            font=("Segoe UI", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        fields = [
            ("Prestamo", self.principal_var, 0),
            ("Interes anual (%)", self.rate_var, 1),
            ("Tiempo", self.term_var, 2),
        ]
        for label, variable, column in fields:
            ttk.Label(self, text=label, font=_LABELS_FONT).grid(
                row=1, column=column, sticky="w", padx=(0, 18)
            )
            entry = ttk.Entry(self, textvariable=variable, width=16, font=_ENTRY_FONT)
            entry.grid(row=2, column=column, sticky="we", padx=(0, 18), pady=(2, 8))

        ttk.Label(self, text="Unidad", font=_LABELS_FONT).grid(
            row=1, column=3, sticky="w", padx=(0, 18)
        )
        unit_box = ttk.Combobox(
            self, textvariable=self.unit_var, values=UNIT_CHOICES,
            state="readonly", width=10, font=_ENTRY_FONT,
        )
        unit_box.grid(row=2, column=3, sticky="we", padx=(0, 18), pady=(2, 8))

        ttk.Label(self, text="Fecha 1ra cuota", font=_LABELS_FONT).grid(
            row=1, column=4, sticky="w", padx=(0, 18)
        )
        ttk.Entry(
            self, textvariable=self.date_var, width=14, font=_ENTRY_FONT
        ).grid(row=2, column=4, sticky="we", padx=(0, 18), pady=(2, 8))

        ttk.Label(self, text="Metodo", font=_LABELS_FONT).grid(
            row=1, column=5, sticky="w"
        )
        method_box = ttk.Combobox(
            self, textvariable=self.method_var, values=METHOD_CHOICES,
            state="readonly", width=22, font=_ENTRY_FONT,
        )
        method_box.grid(row=2, column=5, sticky="we", pady=(2, 8))

        # Botones
        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=6, sticky="w", pady=(8, 0))

        self.calc_button = ttk.Button(
            buttons, text="Calcular", command=self.on_calculate
        )
        self.calc_button.pack(side="left", padx=(0, 8))

        ttk.Button(buttons, text="Limpiar", command=self.on_clear).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(buttons, text="Exportar CSV", command=self.on_export).pack(
            side="left"
        )

        for column in range(6):
            self.columnconfigure(column, weight=1)
        self.columnconfigure(5, weight=1)

    # ------------------------------------------------------------- Metodos
    def get_values(self) -> dict:
        """Devuelve los datos crudos del formulario (aun sin validar)."""
        unit = UNIT_YEARS if self.unit_var.get() == "Anios" else UNIT_MONTHS
        method = (
            METHOD_GERMAN
            if self.method_var.get().startswith("Aleman")
            else METHOD_FRENCH
        )
        return {
            "principal": self.principal_var.get(),
            "rate": self.rate_var.get(),
            "term": self.term_var.get(),
            "unit": unit,
            "method": method,
            "first_payment_date": parse_date(self.date_var.get()),
        }

    def clear_fields(self) -> None:
        self.principal_var.set("")
        self.rate_var.set("")
        self.term_var.set("")
        self.date_var.set(date.today().strftime("%d/%m/%Y"))
