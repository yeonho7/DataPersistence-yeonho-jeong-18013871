from datetime import datetime, timezone
from model.order import Order
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository

VALID_STATUSES = {"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"}


class OrderController:
    def __init__(self, repo: OrderRepository, sample_repo: SampleRepository):
        self._repo = repo
        self._sample_repo = sample_repo

    def place_order(self, sample_id: str, customer: str, quantity: int) -> Order:
        if self._sample_repo.find_by_id(sample_id) is None:
            raise ValueError(f"존재하지 않는 시료 ID: {sample_id}")
        now = datetime.now(timezone.utc)
        order_id = f"ORD-{now.strftime('%Y%m%d%H%M%S%f')}"
        order = Order(order_id=order_id, sample_id=sample_id, customer=customer, quantity=quantity)
        self._repo.create(order)
        return order

    def change_status(self, order_id: str, status: str):
        if status not in VALID_STATUSES:
            raise ValueError(f"유효하지 않은 주문 상태: {status}")
        order = self._repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"존재하지 않는 주문 ID: {order_id}")
        order.status = status
        order.updated_at = datetime.now(timezone.utc).isoformat()
        self._repo.update(order)

    def list_by_status(self, status: str) -> list[Order]:
        return self._repo.find_by_status(status)

    def list_all(self) -> list[Order]:
        return self._repo.find_all()
