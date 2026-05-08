import math
from model.sample import Sample
from repository.sample_repository import SampleRepository


class SampleController:
    def __init__(self, repo: SampleRepository):
        self._repo = repo

    def register(self, sample_id: str, name: str, avg_production_time: float, yield_rate: float, stock: int = 0) -> Sample:
        if self._repo.find_by_id(sample_id) is not None:
            raise ValueError(f"이미 존재하는 시료 ID: {sample_id}")
        s = Sample(sample_id=sample_id, name=name, avg_production_time=avg_production_time, yield_rate=yield_rate, stock=stock)
        self._repo.create(s)
        return s

    def list_all(self) -> list[Sample]:
        return self._repo.find_all()

    def search_by_name(self, name: str) -> list[Sample]:
        return self._repo.find_by_name(name)

    def update_stock(self, sample_id: str, stock: int):
        s = self._repo.find_by_id(sample_id)
        if s is None:
            raise ValueError(f"존재하지 않는 시료 ID: {sample_id}")
        s.stock = stock
        self._repo.update(s)

    def calculate_production_quantity(self, sample_id: str, order_quantity: int) -> int:
        s = self._repo.find_by_id(sample_id)
        if s is None:
            raise ValueError(f"존재하지 않는 시료 ID: {sample_id}")
        shortage = order_quantity - s.stock
        if shortage <= 0:
            return 0
        return math.ceil(shortage / (s.yield_rate * 0.9))
