"""
Servicio de cálculo de tablas de amortización.
Soporta sistema francés (cuota fija) y sistema alemán (capital constante).
"""
from typing import List
from app.schemas.amortization import AmortizationRow


def calcular_tabla_francesa(
    monto: float,
    tasa_anual: float,
    plazo_meses: int,
    cobros_mensuales: float = 0.0,
    cobros_fijos: float = 0.0,
) -> List[dict]:
    """
    Sistema Francés: cuota de capital + interés constante.
    Fórmula: C = P * i / (1 - (1+i)^-n)
    """
    i = tasa_anual / 100 / 12  # tasa mensual
    n = plazo_meses
    if i == 0:
        cuota_ki = monto / n
    else:
        cuota_ki = monto * i / (1 - (1 + i) ** (-n))

    tabla = []
    saldo = monto

    for periodo in range(1, n + 1):
        interes = round(saldo * i, 4)
        capital = round(cuota_ki - interes, 4)
        if periodo == n:
            # Ajuste de último periodo para evitar diferencias de redondeo
            capital = round(saldo, 4)
        cobros = round(cobros_mensuales + (cobros_fijos if periodo == 1 else 0), 4)
        cuota_total = round(capital + interes + cobros, 4)
        saldo_final = round(saldo - capital, 4)

        tabla.append({
            "period": periodo,
            "initial_balance": round(saldo, 4),
            "capital": capital,
            "interest": interes,
            "indirect_charges": cobros,
            "total_payment": cuota_total,
            "final_balance": max(saldo_final, 0.0),
        })
        saldo = saldo_final

    return tabla


def calcular_tabla_alemana(
    monto: float,
    tasa_anual: float,
    plazo_meses: int,
    cobros_mensuales: float = 0.0,
    cobros_fijos: float = 0.0,
) -> List[dict]:
    """
    Sistema Alemán: capital constante en cada período, interés sobre saldo decreciente.
    """
    i = tasa_anual / 100 / 12
    n = plazo_meses
    capital_constante = round(monto / n, 4)

    tabla = []
    saldo = monto

    for periodo in range(1, n + 1):
        interes = round(saldo * i, 4)
        capital = capital_constante
        if periodo == n:
            capital = round(saldo, 4)
        cobros = round(cobros_mensuales + (cobros_fijos if periodo == 1 else 0), 4)
        cuota_total = round(capital + interes + cobros, 4)
        saldo_final = round(saldo - capital, 4)

        tabla.append({
            "period": periodo,
            "initial_balance": round(saldo, 4),
            "capital": capital,
            "interest": interes,
            "indirect_charges": cobros,
            "total_payment": cuota_total,
            "final_balance": max(saldo_final, 0.0),
        })
        saldo = saldo_final

    return tabla


def calcular_cobros_indirectos(monto: float, cobros: list) -> tuple[float, float]:
    """
    Retorna (cobros_mensuales, cobros_fijos).
    Cobros con is_monthly=True y is_percentage=True → % del monto / 12.
    Cobros con is_monthly=True y is_percentage=False → valor fijo mensual.
    Cobros con is_monthly=False → cobro único en el primer período.
    """
    mensuales = 0.0
    fijos = 0.0
    for cobro in cobros:
        if not cobro.is_active:
            continue
        if cobro.is_monthly:
            if cobro.is_percentage:
                mensuales += monto * cobro.value / 100 / 12
            else:
                mensuales += cobro.value
        else:
            if cobro.is_percentage:
                fijos += monto * cobro.value / 100
            else:
                fijos += cobro.value
    return round(mensuales, 4), round(fijos, 4)
