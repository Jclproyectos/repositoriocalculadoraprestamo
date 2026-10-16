"""Grafico del saldo y de los intereses dibujado sobre un Canvas de Tkinter."""

from __future__ import annotations

from decimal import Decimal

from .models import AmortizationResult, LoanInput

PADDING = 45
COLOR_BALANCE = "#2563eb"
COLOR_INTEREST = "#f59e0b"
COLOR_AXIS = "#64748b"
COLOR_GRID = "#e2e8f0"
COLOR_TEXT = "#334155"


def draw_chart(canvas, loan: LoanInput, result: AmortizationResult) -> None:
    """Redibuja el grafico: saldo restante (linea) e interes de cada cuota (barras)."""
    canvas.delete("all")
    rows = result.rows
    if not rows:
        return

    canvas.update_idletasks()
    width = max(canvas.winfo_width(), 400)
    height = max(canvas.winfo_height(), 260)

    max_value = float(loan.principal)
    max_payment = max((float(r.payment) for r in rows), default=0.0)
    max_value = max(max_value, max_payment, 1.0)

    count = len(rows)

    def x_pos(index: float) -> float:
        usable = width - 2 * PADDING
        return PADDING + usable * index / max(count - 1, 1)

    def y_pos(value: float) -> float:
        usable = height - 2 * PADDING
        return height - PADDING - usable * (value / max_value)

    # Rejilla y ejes
    for step in range(5):
        value = max_value * step / 4
        y = y_pos(value)
        canvas.create_line(PADDING, y, width - PADDING, y, fill=COLOR_GRID)
        canvas.create_text(
            PADDING - 8, y, text=f"{value:,.0f}", anchor="e",
            fill=COLOR_TEXT, font=("Segoe UI", 8),
        )
    canvas.create_line(PADDING, PADDING, PADDING, height - PADDING, fill=COLOR_AXIS)
    canvas.create_line(PADDING, height - PADDING, width - PADDING, height - PADDING, fill=COLOR_AXIS)

    # Barras de interes por cuota
    bar_width = max(1.0, (width - 2 * PADDING) / (count * 1.8))
    for i, row in enumerate(rows):
        interest = float(row.interest)
        if interest <= 0:
            continue
        x = x_pos(i) - bar_width / 2
        y = y_pos(interest)
        canvas.create_rectangle(
            x, y, x + bar_width, height - PADDING,
            fill=COLOR_INTEREST, outline="",
        )

    # Linea de saldo restante
    points = []
    for i, row in enumerate(rows):
        points.extend([x_pos(i), y_pos(float(row.balance))])
    if len(points) >= 4:
        canvas.create_line(*points, fill=COLOR_BALANCE, width=2, smooth=True)

    # Etiqueta de la ultima fecha
    canvas.create_text(
        width - PADDING, height - PADDING + 14,
        text=rows[-1].date.strftime("%m/%Y"),
        anchor="e", fill=COLOR_TEXT, font=("Segoe UI", 8),
    )
    canvas.create_text(
        PADDING, height - PADDING + 14,
        text=rows[0].date.strftime("%m/%Y"),
        anchor="w", fill=COLOR_TEXT, font=("Segoe UI", 8),
    )

    # Leyenda
    canvas.create_rectangle(width - 210, 10, width - 196, 24, fill=COLOR_BALANCE, outline="")
    canvas.create_text(width - 206, 17, text="Saldo", anchor="w",
                       fill=COLOR_TEXT, font=("Segoe UI", 9))
    canvas.create_rectangle(width - 130, 10, width - 116, 24, fill=COLOR_INTEREST, outline="")
    canvas.create_text(width - 126, 17, text="Interes por cuota", anchor="w",
                       fill=COLOR_TEXT, font=("Segoe UI", 9))
