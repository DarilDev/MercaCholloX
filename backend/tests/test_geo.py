from app.services.geo import haversine_km


def test_haversine_zero_distance():
    assert haversine_km(40.4168, -3.7038, 40.4168, -3.7038) == 0


def test_haversine_known_distance():
    # Madrid (Puerta del Sol) -> Barcelona (Plaça Catalunya), ~504km en línea recta
    km = haversine_km(40.4168, -3.7038, 41.3874, 2.1686)
    assert 495 < km < 515
