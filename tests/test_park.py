from python_park_console import ParkService, TicketType

def test_sell_tickets_pago_insuficiente(capsys):
    svc = ParkService()
    svc.create_attraction("Montaña", 1, True)

    tickets = svc.sell_tickets([TicketType.ADULT], cash=20.0)  # 50 > 20
    captured = capsys.readouterr().out

    assert tickets == []
    assert "Efectivo insuficiente" in captured
    assert svc.revenue == 0.0
    assert len(svc.tickets) == 0


def test_reglas_de_ingreso_cerrada_sin_cupos_y_reuso(capsys):
    svc = ParkService()
    a = svc.create_attraction("Río Aventura", 1, False)  # empieza cerrada
    t = svc.sell_tickets([TicketType.ADULT], cash=100.0)[0]

    # 1) Cerrada
    ok1 = svc.enter(t.id, a.id)
    out1 = capsys.readouterr().out
    assert ok1 is False
    assert "Atracción cerrada" in out1

    # Abrir y entrar (consume 1 cupo)
    assert svc.set_open(a.id, True) is True
    ok2 = svc.enter(t.id, a.id)
    assert ok2 is True
    assert svc.attractions[a.id].capacity == 0

    # 2) Reusar mismo ticket en misma atracción
    ok3 = svc.enter(t.id, a.id)
    out3 = capsys.readouterr().out
    assert ok3 is False
    assert "Ticket ya usado" in out3

    # 3) Sin cupos con otro ticket
    t2 = svc.sell_tickets([TicketType.ADULT], cash=100.0)[0]
    ok4 = svc.enter(t2.id, a.id)
    out4 = capsys.readouterr().out
    assert ok4 is False
    assert "Sin cupos" in out4


def test_crear_y_actualizar_atraccion():
    svc = ParkService()
    a = svc.create_attraction("Casa del Arriero (VR)", 5, True)

    # Cambiar estado
    assert svc.set_open(a.id, False) is True
    assert svc.attractions[a.id].open is False
    assert svc.set_open(a.id, True) is True
    assert svc.attractions[a.id].open is True

    # Cambiar capacidad válida
    assert svc.set_capacity(a.id, 12) is True
    assert svc.attractions[a.id].capacity == 12

    # Capacidad inválida
    assert svc.set_capacity(a.id, -1) is False
    assert svc.attractions[a.id].capacity == 12
