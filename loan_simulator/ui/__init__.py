"""Interfaz grafica del simulador (paquete UI).

Toda la logica de presentacion vive aqui; no contiene formulas
financieras (esas estan en ``loan_simulator.calculator``).
"""

from .main_window import LoanSimulatorApp

__all__ = ["LoanSimulatorApp"]
