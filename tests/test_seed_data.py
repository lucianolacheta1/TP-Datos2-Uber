"""Tests del seed determinista (scripts/seed_data).

NO tocan bases de datos: verifican que el plan determinista del seed produzca
EXACTAMENTE los resultados documentados para los 7 casos de uso. Asi, si alguien
toca el seed y rompe la coherencia con la demo, estos tests fallan.
"""
from collections import Counter

from scripts.seed_data import (
    USUARIOS, CONDUCTORES, VEHICULOS,
    PLAN_VIAJES, DURACIONES, METODOS, RATING_USER, RATING_COND,
)


def test_caso_1_top3_resenadores_es_juan_maria_carlos():
    # El autor de la resena U_A_C es el pasajero (idx_user); 1 resena por viaje.
    conteo = Counter(idx_user for idx_user, _, _ in PLAN_VIAJES)
    top3 = conteo.most_common(3)
    nombres = [USUARIOS[idx][1] for idx, _ in top3]
    cantidades = [c for _, c in top3]
    assert nombres == ["Juan Pérez", "María García", "Carlos López"]
    assert cantidades == [4, 3, 2]
    # Nadie fuera del top 3 llega a 2 -> 3er puesto sin empate (orden estable).
    assert all(c <= 1 for idx, c in conteo.items() if idx not in (0, 1, 2))


def test_caso_2_metodo_menos_usado_es_billetera():
    conteo = Counter(METODOS)
    menos = min(conteo, key=conteo.get)
    assert menos == "BILLETERA_VIRTUAL"
    assert conteo["BILLETERA_VIRTUAL"] == 2
    assert conteo["EFECTIVO"] == 5
    assert conteo["TARJETA"] == 9


def test_caso_3_inactivos_son_carolina_y_roberto():
    UMBRAL_DIAS = 30
    activos_recientes = {
        idx_cond for _, idx_cond, dias in PLAN_VIAJES if dias < UMBRAL_DIAS
    }
    inactivos = [
        CONDUCTORES[i][1]
        for i in range(len(CONDUCTORES))
        if i not in activos_recientes
    ]
    assert sorted(inactivos) == sorted(["Carolina Vega", "Roberto Núñez"])


def test_caso_4_promedio_duracion_es_22():
    assert sum(DURACIONES) / len(DURACIONES) == 22.0


def test_caso_5_coincidencias_son_exactamente_3():
    conteo = Counter((u, c) for u, c, _ in PLAN_VIAJES)
    pares_repetidos = {par: n for par, n in conteo.items() if n >= 2}
    # Solo Juan-Ana(4), Maria-Luis(3), Carlos-Beatriz(2). Nada de parasitos.
    assert pares_repetidos == {(0, 0): 4, (1, 1): 3, (2, 2): 2}


def test_caso_6_toyota_patente_d_son_3():
    n = sum(
        1
        for (_, placa, marca, *_) in VEHICULOS
        if marca == "Toyota" and placa.endswith("D")
    )
    assert n == 3


def test_caso_7_rating_extremo_6_cincos_4_unos():
    todos = RATING_USER + RATING_COND
    assert todos.count(5) == 6
    assert todos.count(1) == 4
    # Extremos = rating 5 o rating < 2 (no hay rating 2 en el seed).
    assert sum(1 for r in todos if r == 5 or r < 2) == 10


def test_totales_del_dataset_son_coherentes():
    assert len(PLAN_VIAJES) == 16
    assert len(DURACIONES) == 16
    assert len(METODOS) == 16
    assert len(RATING_USER) == 16
    assert len(RATING_COND) == 16
