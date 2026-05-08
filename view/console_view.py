from model.sample import Sample
from model.order import Order


class ConsoleView:
    def show_samples(self, samples: list[Sample]):
        if not samples:
            print("  (시료 없음)")
            return
        print(f"  {'ID':<10} {'이름':<15} {'생산시간(분)':<12} {'수율':<8} {'재고'}")
        print("  " + "-" * 55)
        for s in samples:
            print(f"  {s.sample_id:<10} {s.name:<15} {s.avg_production_time:<12} {s.yield_rate:<8} {s.stock}")

    def show_orders(self, orders: list[Order]):
        if not orders:
            print("  (주문 없음)")
            return
        print(f"  {'주문ID':<28} {'시료ID':<10} {'고객':<10} {'수량':<6} {'상태'}")
        print("  " + "-" * 70)
        for o in orders:
            print(f"  {o.order_id:<28} {o.sample_id:<10} {o.customer:<10} {o.quantity:<6} {o.status}")

    def show_message(self, message: str):
        print(f"[INFO] {message}")

    def show_error(self, message: str):
        print(f"[ERROR] {message}")
