from app.services.scoring import detour_extra, evaluate, fuel_cost, time_cost


def test_detour_extra_sin_trabajo_es_ida_y_vuelta():
    km, min_ = detour_extra(home_to_candidate_km=3.0, home_to_candidate_min=6.0)
    assert km == 6.0
    assert min_ == 12.0


def test_detour_extra_con_trabajo_tienda_de_camino():
    # casa->trabajo directo son 20km/25min; la candidata está de camino,
    # así que el desvío real debería ser pequeño o cero
    km, min_ = detour_extra(
        home_to_candidate_km=8.0,
        home_to_candidate_min=10.0,
        candidate_to_work_km=12.0,
        candidate_to_work_min=15.0,
        home_to_work_km=20.0,
        home_to_work_min=25.0,
    )
    assert km == 0.0
    assert min_ == 0.0


def test_detour_extra_con_trabajo_desvio_real():
    km, min_ = detour_extra(
        home_to_candidate_km=15.0,
        home_to_candidate_min=20.0,
        candidate_to_work_km=15.0,
        candidate_to_work_min=20.0,
        home_to_work_km=20.0,
        home_to_work_min=25.0,
    )
    assert km == 10.0
    assert min_ == 15.0


def test_detour_extra_nunca_negativo():
    # ruido de OSRM: la "candidata de camino" podría salir ligerísimamente
    # negativa por rutas no idénticas — no debe dar un desvío negativo
    km, min_ = detour_extra(
        home_to_candidate_km=5.0,
        home_to_candidate_min=8.0,
        candidate_to_work_km=10.0,
        candidate_to_work_min=12.0,
        home_to_work_km=15.5,  # 5+10=15 < 15.5
        home_to_work_min=20.5,
    )
    assert km == 0.0
    assert min_ == 0.0


def test_fuel_cost():
    # 10km extra, 6.5 L/100km, 1.80 EUR/L -> 0.65L * 1.80 = 1.17
    assert fuel_cost(10.0, 6.5, 1.80) == 1.17


def test_time_cost():
    # 15 min extra, 8 EUR/h -> 0.25h * 8 = 2.0
    assert time_cost(15.0, 8.0) == 2.0


def test_evaluate_vale_la_pena():
    result = evaluate(
        basket_usual_eur=10.0,
        basket_candidate_eur=6.0,  # ahorro cesta: 4.0
        home_to_candidate_km=2.0,
        home_to_candidate_min=4.0,  # sin trabajo -> ida/vuelta: 4km, 8min
        consumption_l_per_100km=6.5,
        fuel_price_eur_l=1.80,
        hourly_value_eur=8.0,
    )
    # fuel_cost = (4/100)*6.5*1.80 = 0.468 -> 0.47
    # time_cost = (8/60)*8 = 1.0667 -> 1.07
    # net = 4.0 - 0.47 - 1.07 = 2.46
    assert result.fuel_cost_eur == 0.47
    assert result.time_cost_eur == 1.07
    assert result.basket_savings_eur == 4.0
    assert result.net_savings_eur == 2.46
    assert result.worth_it is True


def test_evaluate_no_vale_la_pena_desvio_caro():
    result = evaluate(
        basket_usual_eur=10.0,
        basket_candidate_eur=9.5,  # ahorro cesta: solo 0.5
        home_to_candidate_km=20.0,
        home_to_candidate_min=25.0,  # desvío caro
        consumption_l_per_100km=6.5,
        fuel_price_eur_l=1.80,
        hourly_value_eur=8.0,
    )
    assert result.basket_savings_eur == 0.5
    assert result.net_savings_eur < 0
    assert result.worth_it is False


def test_evaluate_umbral_evita_falso_positivo_por_redondeo():
    # ahorro neto minúsculo (0.30) no debería marcarse como "vale la pena"
    result = evaluate(
        basket_usual_eur=1.30,
        basket_candidate_eur=1.00,
        home_to_candidate_km=0.0,
        home_to_candidate_min=0.0,
        consumption_l_per_100km=6.5,
        fuel_price_eur_l=1.80,
        hourly_value_eur=8.0,
    )
    assert result.net_savings_eur == 0.3
    assert result.worth_it is False
