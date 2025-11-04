# bench_park.py
from time import perf_counter
from random import Random
from park_console import ParkService, TicketType, seed

def run_once(orders: int) -> float:
    svc = ParkService()
    seed(svc)
    rnd = Random(42)

    t0 = perf_counter()
    for _ in range(orders):
        k = 1 + rnd.randint(0, 2)  # 1..3 tickets
        types = [rnd.choice([TicketType.ADULT, TicketType.CHILD, TicketType.SENIOR]) for _ in range(k)]
        total = sum(t.value for t in types)
        created = svc.sell_tickets(types, cash=total)
        if created:
            svc.enter(created[0].id, 101)
    t1 = perf_counter()
    return (t1 - t0) * 1000.0  # ms

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders", type=int, default=5000)
    ap.add_argument("--runs", type=int, default=3)
    args = ap.parse_args()

    # warm-up
    run_once(1000)

    for r in range(1, args.runs + 1):
        ms = run_once(args.orders)
        per_op = ms / args.orders
        ops = (args.orders * 1000.0) / ms
        print(f"Run {r}: {args.orders:,} ops | total={ms:.0f} ms | {per_op:.3f} ms/op | {ops:.1f} ops/s")

if __name__ == "__main__":
    main()
