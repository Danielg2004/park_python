
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set
import uuid

class TicketType(Enum):
    ADULT = 50.0
    CHILD = 30.0
    SENIOR = 35.0

@dataclass
class Attraction:
    id: int
    name: str
    open: bool
    capacity: int
    total_entries: int = 0

    def __str__(self) -> str:
        state = "ABIERTA" if self.open else "CERRADA"
        return f"#{self.id} | {self.name} | {state} | cupos:{self.capacity} | ingresos:{self.total_entries}"

@dataclass
class Ticket:
    type: TicketType
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())
    used_attractions: Set[int] = field(default_factory=set)

class ParkService:
    def __init__(self) -> None:
        self._seq = 100
        self.attractions: Dict[int, Attraction] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.revenue: float = 0.0

    # ---- Atracciones ----
    def create_attraction(self, name: str, cap: int, open_: bool) -> Attraction:
        self._seq += 1
        a = Attraction(self._seq, name, open_, cap)
        self.attractions[a.id] = a
        return a

    def list_attractions(self) -> None:
        if not self.attractions:
            print("Sin atracciones.")
            return
        for a in self.attractions.values():
            print(a)

    def set_open(self, id_: int, open_: bool) -> bool:
        a = self.attractions.get(id_)
        if not a:
            return False
        a.open = open_
        return True

    def set_capacity(self, id_: int, cap: int) -> bool:
        a = self.attractions.get(id_)
        if not a or cap < 0:
            return False
        a.capacity = cap
        return True

    # ---- Venta de tickets (efectivo simple) ----
    def sell_tickets(self, types: List[TicketType], cash: float) -> List[Ticket]:
        if not types:
            print("No hay tickets.")
            return []
        total = sum(t.value for t in types)
        if cash + 1e-9 < total:
            print("Efectivo insuficiente. Cancelado.")
            return []
        print(f"TOTAL: {total:.2f}  | Pago OK. Cambio: {cash - total:.2f}")

        created: List[Ticket] = []
        for t in types:
            tk = Ticket(t)
            self.tickets[tk.id] = tk
            created.append(tk)

        self.revenue += total
        print("Tickets generados:")
        for tk in created:
            print(f" - {tk.id} ({tk.type.name})")
        return created

    # ---- Ingreso a atracción ----
    def enter(self, ticket_id: str, attraction_id: int) -> bool:
        t = self.tickets.get(ticket_id)
        a = self.attractions.get(attraction_id)
        if not t:
            print("Ticket no existe."); return False
        if not a:
            print("Atracción no existe."); return False
        if not a.open:
            print("Atracción cerrada."); return False
        if a.capacity <= 0:
            print("Sin cupos."); return False
        if attraction_id in t.used_attractions:
            print("Ticket ya usado en esta atracción."); return False

        a.capacity -= 1
        a.total_entries += 1
        t.used_attractions.add(attraction_id)
        print(f"Ingreso a '{a.name}' OK. Cupos restantes: {a.capacity}")
        return True

    # ---- Reporte ----
    def report(self) -> None:
        print("=== REPORTE ===")
        print(f"Ingresos: {self.revenue:.2f}")
        print(f"Tickets vendidos: {len(self.tickets)}")
        for a in self.attractions.values():
            estado = "ABIERTA" if a.open else "CERRADA"
            print(f" - {a.name}: {a.total_entries} ingresos | cap:{a.capacity} | {estado}")

# -------- Utilidades de consola --------
def read_int(prompt: str = "") -> int:
    if prompt: print(prompt, end="")
    while True:
        try:
            return int(input().strip())
        except Exception:
            print("Número inválido: ", end="")

def read_float(prompt: str = "") -> float:
    if prompt: print(prompt, end="")
    while True:
        try:
            return float(input().strip())
        except Exception:
            print("Número inválido: ", end="")

def ask_type() -> TicketType:
    print("1) ADULT  2) CHILD  3) SENIOR")
    while True:
        print("Tipo: ", end="")
        op = read_int()
        if op == 1: return TicketType.ADULT
        if op == 2: return TicketType.CHILD
        if op == 3: return TicketType.SENIOR
        print("Opción inválida.")

def seed(svc: ParkService) -> None:
    svc.create_attraction("Montaña del Café", 10, True)
    svc.create_attraction("Río Aventura", 8, True)
    svc.create_attraction("Casa del Arriero (VR)", 5, False)

def menu() -> None:
    print("\n=== PARQUE - Consola (Python corta) ===")
    print("1) Listar atracciones")
    print("2) Crear atraccion")
    print("3) Abrir/Cerrar atraccion")
    print("4) Cambiar capacidad")
    print("5) Vender tickets")
    print("6) Ingresar a atraccion")
    print("7) Reporte")
    print("0) Salir")
    print("Opcion: ", end="")

def main() -> None:
    svc = ParkService()
    seed(svc)

    run = True
    while run:
        menu()
        op = read_int()
        if op == 1:
            svc.list_attractions()
        elif op == 2:
            name = input("Nombre: ").strip()
            cap = read_int("Capacidad: ")
            open_ = read_int("¿Abrir? (1=Sí,0=No): ") == 1
            print("Creada:", svc.create_attraction(name, cap, open_))
        elif op == 3:
            id_ = read_int("ID: ")
            open_ = read_int("1=ABRIR, 0=CERRAR: ") == 1
            print("Actualizada." if svc.set_open(id_, open_) else "No existe.")
        elif op == 4:
            id_ = read_int("ID: ")
            cap = read_int("Nueva capacidad: ")
            print("OK" if svc.set_capacity(id_, cap) else "No existe/cap inválida.")
        elif op == 5:
            types: List[TicketType] = []
            while True:
                add = read_int("Agregar ticket? (1=Sí,0=No): ")
                if add != 1:
                    break
                types.append(ask_type())
            if types:
                total = sum(t.value for t in types)
                cash = read_float(f"TOTAL: {total:.2f}  | Ingrese efectivo: ")
                svc.sell_tickets(types, cash)
            else:
                print("No hay tickets.")
        elif op == 6:
            tid = input("ID ticket: ").strip().upper()
            aid = read_int("ID atracción: ")
            svc.enter(tid, aid)
        elif op == 7:
            svc.report()
        elif op == 0:
            run = False
            print("Adiós!")
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
