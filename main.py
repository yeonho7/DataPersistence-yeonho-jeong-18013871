from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from view.console_view import ConsoleView

view = ConsoleView()
sample_repo = SampleRepository()
order_repo = OrderRepository()
sample_ctrl = SampleController(sample_repo)
order_ctrl = OrderController(order_repo, sample_repo)

# 시료 3종 등록 (이미 존재하면 스킵)
samples = [
    ("S-001", "알파시료", 5.0, 0.9, 30),
    ("S-002", "베타시료", 3.5, 0.85, 15),
    ("S-003", "감마시료", 7.0, 0.75, 0),
]
for sid, name, pt, yr, stock in samples:
    try:
        sample_ctrl.register(sid, name, pt, yr, stock)
        view.show_message(f"시료 등록: {sid} ({name})")
    except ValueError as e:
        view.show_message(str(e))

print("\n[시료 목록]")
view.show_samples(sample_ctrl.list_all())

# 주문 생성 (S-001, RESERVED)
order = order_ctrl.place_order(sample_id="S-001", customer="고객A", quantity=50)
view.show_message(f"주문 생성: {order.order_id} (상태: {order.status})")

# 주문 상태 변경 RESERVED → CONFIRMED
order_ctrl.change_status(order.order_id, "CONFIRMED")
view.show_message(f"주문 상태 변경: {order.order_id} → CONFIRMED")

print("\n[주문 목록]")
view.show_orders(order_ctrl.list_all())

# 생산량 계산 (S-003, 주문 20개, 재고 0)
qty = sample_ctrl.calculate_production_quantity("S-003", order_quantity=20)
view.show_message(f"S-003 생산 필요량: {qty}개 (주문 20개, 재고 0개, 수율 0.75)")
