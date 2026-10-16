"""Simulador de prestamos con tabla de amortizacion.

Arquitectura modular:
    - models      : estructuras de datos
    - validators  : validacion de la entrada del usuario
    - calculator  : logica financiera (amortizacion e interes)
    - exporter    : exportacion a CSV
    - chart       : grafico del saldo/intereses
    - ui          : interfaz grafica (Tkinter)
"""

__version__ = "1.0.0"
