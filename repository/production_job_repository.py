import json
import os
from dataclasses import asdict
from model.production_job import ProductionJob
from repository.base_repository import BaseRepository


class ProductionJobRepository(BaseRepository):
    def __init__(self, filepath: str = "data/production_jobs.json"):
        self._filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(filepath):
            self._write([])

    def _read(self) -> list[dict]:
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: list[dict]):
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, entity: ProductionJob):
        data = self._read()
        data.append(asdict(entity))
        self._write(data)

    def find_by_id(self, entity_id: str) -> ProductionJob | None:
        for item in self._read():
            if item["job_id"] == entity_id:
                return ProductionJob(**item)
        return None

    def find_all(self) -> list[ProductionJob]:
        return [ProductionJob(**item) for item in self._read()]

    def update(self, entity: ProductionJob) -> bool:
        data = self._read()
        for i, item in enumerate(data):
            if item["job_id"] == entity.job_id:
                data[i] = asdict(entity)
                self._write(data)
                return True
        return False

    def delete(self, entity_id: str) -> bool:
        data = self._read()
        new_data = [item for item in data if item["job_id"] != entity_id]
        if len(new_data) < len(data):
            self._write(new_data)
            return True
        return False
