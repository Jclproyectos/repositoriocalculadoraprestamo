"""Punto de entrada del Simulador de Prestamos.

Ejecutar con:  python main.py
"""

from loan_simulator.ui import LoanSimulatorApp


def main() -> None:
    app = LoanSimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
