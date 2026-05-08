import os
import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository

TEST_FILE = "data/test_samples.json"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def repo():
    return SampleRepository(TEST_FILE)


def test_sample_creation():
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9)
    assert s.sample_id == "S-001"
    assert s.name == "알파"
    assert s.avg_production_time == 5.0
    assert s.yield_rate == 0.9


def test_sample_default_stock():
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9)
    assert s.stock == 0


def test_repository_create_and_find_by_id(repo):
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9)
    repo.create(s)
    found = repo.find_by_id("S-001")
    assert found.sample_id == "S-001"
    assert found.name == "알파"


def test_repository_find_all(repo):
    repo.create(Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9))
    repo.create(Sample(sample_id="S-002", name="베타", avg_production_time=3.0, yield_rate=0.8))
    assert len(repo.find_all()) == 2


def test_repository_update(repo):
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9, stock=0)
    repo.create(s)
    s.stock = 50
    repo.update(s)
    found = repo.find_by_id("S-001")
    assert found.stock == 50


def test_repository_delete(repo):
    repo.create(Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9))
    repo.delete("S-001")
    assert repo.find_by_id("S-001") is None


def test_repository_find_by_name_partial_match(repo):
    repo.create(Sample(sample_id="S-001", name="알파시료", avg_production_time=5.0, yield_rate=0.9))
    repo.create(Sample(sample_id="S-002", name="베타시료", avg_production_time=3.0, yield_rate=0.8))
    results = repo.find_by_name("알파")
    assert len(results) == 1
    assert results[0].sample_id == "S-001"


def test_repository_persistence_across_instances():
    repo1 = SampleRepository(TEST_FILE)
    repo1.create(Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9))

    repo2 = SampleRepository(TEST_FILE)
    found = repo2.find_by_id("S-001")
    assert found is not None
    assert found.name == "알파"
