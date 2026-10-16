"""Ventana principal: conecta el formulario, el calculo, la tabla y el grafico."""

from __future__ import annotations

from tkinter import Canvas, StringVar, Tk, filedialog, messagebox, ttk

from ..calculator import calculate
from ..chart import draw_chart
from ..exporter import export_schedule
from ..models import AmortizationResult, LoanInput
from ..validators import LoanValidationError, build_loan
from .input_panel import InputPanel
from .summary_view import SummaryView
from .table_view import ScheduleTable

BG = "#f1f5f9"
PANEL_BG = "#ffffff"


class LoanSimulatorApp(Tk):
    """Ventana principal de la aplicacion."""

    def __init__(self):
        super().__init__()
        self.title("Simulador de Prestamos - Tabla de Amortizacion")
        self.geometry("1100x780")
        self.minsize(940, 640)
        self.configure(background=BG)

        self._loan: LoanInput | None = None
        self._result: AmortizationResult | None = None

        self._setup_style()
        self._build_ui()

    # ------------------------------------------------------------- Estilos
    def _setup_style(self) -> None:
        style = ttk.Style(self)
        for theme in ("vista", "clam", "default"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

        style.configure(".", background=BG, font=("Segoe UI", 9))
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", padding=(14, 6), font=("Segoe UI", 9))
        style.configure("Card.TFrame", background=PANEL_BG)
        style.configure("Status.TLabel", background="#e2e8f0", padding=(10, 6))

    # ----------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        # Panel de entrada
        self.input_panel = InputPanel(
            self,
            on_calculate=self._on_calculate,
            on_clear=self._on_clear,
            on_export=self._on_export,
        )
        self.input_panel.pack(fill="x", padx=14, pady=(14, 8))

        # Resumen
        summary_container = ttk.Frame(self, style="Card.TFrame", padding=1)
        summary_container.pack(fill="x", padx=14, pady=(0, 10))
        self.summary = SummaryView(summary_container)
        self.summary.pack(fill="x")

        # Pestanas: tabla / grafico
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.table = ScheduleTable(notebook)
        notebook.add(self.table, text="  Tabla de amortizacion  ")

        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="  Grafico  ")
        self.chart = Canvas(chart_frame, background=PANEL_BG, highlightthickness=0)
        self.chart.pack(fill="both", expand=True, padx=6, pady=6)
        self.chart.bind("<Configure>", self._on_chart_resize)

        # Barra de estado
        self.status_var = StringVar(value="Complete los datos y pulse 'Calcular'.")
        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel").pack(
            fill="x", side="bottom"
        )

    # ----------------------------------------------------------- Acciones
    def _on_calculate(self) -> None:
        try:
            values = self.input_panel.get_values()
            loan = build_loan(
                principal_text=values["principal"],
                rate_text=values["rate"],
                term_text=values["term"],
                unit=values["unit"],
                method=values["method"],
                first_payment_date=values["first_payment_date"],
            )
            result = calculate(loan)
        except LoanValidationError as error:
            messagebox.showerror("Datos invalidos", str(error), parent=self)
            return
        except Exception as error:  # proteccion general de la GUI
            messagebox.showerror("Error inesperado", str(error), parent=self)
            return

        self._loan = loan
        self._result = result
        self.summary.render(loan, result)
        self.table.render(result, loan.principal)
        draw_chart(self.chart, loan, result)
        self.status_var.set(
            f"Simulacion generada: {len(result.rows)} cuotas | "
            f"Total a pagar: {result.total_paid:,.2f} | "
            f"Total intereses: {result.total_interest:,.2f}"
        )

    def _on_clear(self) -> None:
        self.input_panel.clear_fields()
        self.table.clear()
        self.summary.clear()
        self.chart.delete("all")
        self._loan = None
        self._result = None
        self.status_var.set("Formulario y resultados limpiados.")

    def _on_export(self) -> None:
        if not self._result or not self._loan:
            messagebox.showwarning(
                "Sin datos", "Primero debe calcular una simulacion.", parent=self
            )
            return

        path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar tabla de amortizacion",
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv"), ("Todos los archivos", "*.*"),
                       ("Texto", "*.txt")],
        )
        if not path:
            return

        try:
            export_schedule(path, self._loan, self._result)
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error), parent=self)
            return

        self.status_var.set(f"Tabla exportada a: {path}")
        messagebox.showinfo("Exportado", f"Archivo guardado en:\n{path}", parent=self)

    def _on_chart_resize(self, _event) -> None:
        if self._loan and self._result:
            draw_chart(self.chart, self._loan, self._result)
