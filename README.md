# Simulador de Préstamos con Tabla de Amortización

Programa de escritorio (Python + Tkinter) que genera la **tabla de amortización**
con la cuota, el **interés**, la amortización de capital y el saldo restante,
a partir de tres datos que ingresa el usuario: **préstamo, interés y tiempo**.

## Requisitos

- Python 3.10 o superior (incluye `tkinter` por defecto).

## Ejecución

```bash
python main.py
```

Pruebas del motor de cálculo:

```bash
python -m unittest discover -s tests -v
```

## Datos de entrada

| Campo           | Ejemplo            |
|-----------------|--------------------|
| Préstamo        | `25000`            |
| Interés anual % | `18`               |
| Tiempo          | `36` + Meses/Años  |
| Método          | Francés / Alemán   |
| Fecha 1ª cuota  | `01/11/2026`       |

- **Francés (cuota fija):** cuota constante; al inicio se paga más interés.
- **Alemán (amortización fija):** se amortiza capital fijo; la cuota baja cada mes.

La tasa anual se convierte a tasa mensual: `mensual = anual / 12`.
Todas las operaciones usan `decimal.Decimal` (sin errores de coma flotante en dinero).

## Estructura modular

```
G:\tarea
├── main.py                        # punto de entrada (solo arranca la GUI)
├── loan_simulator/
│   ├── __init__.py                # descripción de la arquitectura
│   ├── models.py                  # datos: LoanInput, PaymentRow, AmortizationResult
│   ├── validators.py              # validación/conversión de lo que escribe el usuario
│   ├── calculator.py              # lógica financiera (francés y alemán)
│   ├── exporter.py                # exportación a CSV
│   ├── chart.py                   # gráfico de saldo/intereses (Canvas)
│   └── ui/                        # INTERFAZ GRÁFICA (sin fórmulas)
│       ├── __init__.py
│       ├── main_window.py         # ventana principal, conecta todo
│       ├── input_panel.py         # formulario de entrada
│       ├── table_view.py          # tabla (Treeview) de amortización
│       └── summary_view.py        # resumen de totales
└── tests/
    └── test_calculator.py         # pruebas unitarias sin GUI
```

**Regla de la arquitectura:** `ui/` nunca calcula; solo llama a `validators`
y `calculator`, y pinta lo que éstos devuelven. Así la lógica se puede probar
y reutilizar sin interfaz (como se ve en `tests/`).

## Funciones de la interfaz

- **Calcular** → llena la tabla (Nº, Fecha, Cuota, Interés, Amortización, Saldo)
  con fila de totales, el resumen y el gráfico del saldo.
- **Limpiar** → reinicia el formulario y los resultados.
- **Exportar CSV** → guarda la tabla completa (separador `;`, listo para Excel).
- Pestaña **Gráfico** → línea de saldo restante y barras de interés por cuota.
