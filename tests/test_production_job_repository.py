import os
import pytest
from model.production_job import ProductionJob
from repository.production_job_repository import ProductionJobRepository

TEST_FILE = "data/test_production_jobs.json"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def repo():
    return ProductionJobRepository(TEST_FILE)


def test_create_and_find_by_id(repo):
    job = ProductionJob(job_id="JOB-0001", order_id="ORD-001", actual_production_qty=100, estimated_time_min=50, queue_position=1)
    repo.create(job)
    found = repo.find_by_id("JOB-0001")
    assert found is not None
    assert found.job_id == "JOB-0001"
    assert found.order_id == "ORD-001"


def test_find_all(repo):
    repo.create(ProductionJob(job_id="JOB-0001", order_id="ORD-001", actual_production_qty=100, estimated_time_min=50, queue_position=1))
    repo.create(ProductionJob(job_id="JOB-0002", order_id="ORD-002", actual_production_qty=200, estimated_time_min=80, queue_position=2))
    assert len(repo.find_all()) == 2


def test_update(repo):
    job = ProductionJob(job_id="JOB-0001", order_id="ORD-001", actual_production_qty=100, estimated_time_min=50, queue_position=1)
    repo.create(job)
    job.queue_position = 3
    repo.update(job)
    found = repo.find_by_id("JOB-0001")
    assert found.queue_position == 3


def test_delete(repo):
    repo.create(ProductionJob(job_id="JOB-0001", order_id="ORD-001", actual_production_qty=100, estimated_time_min=50, queue_position=1))
    repo.delete("JOB-0001")
    assert repo.find_by_id("JOB-0001") is None


def test_update_not_found_returns_false(repo):
    job = ProductionJob(job_id="JOB-9999", order_id="ORD-999", actual_production_qty=0, estimated_time_min=0, queue_position=0)
    assert repo.update(job) is False


def test_delete_not_found_returns_false(repo):
    assert repo.delete("JOB-9999") is False


def test_persistence_across_instances():
    repo1 = ProductionJobRepository(TEST_FILE)
    repo1.create(ProductionJob(job_id="JOB-0001", order_id="ORD-001", actual_production_qty=100, estimated_time_min=50, queue_position=1))
    repo2 = ProductionJobRepository(TEST_FILE)
    found = repo2.find_by_id("JOB-0001")
    assert found is not None
    assert found.order_id == "ORD-001"
