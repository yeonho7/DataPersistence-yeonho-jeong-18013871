import pytest
from model.sample import Sample


def test_sample_creation():
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9)
    assert s.sample_id == "S-001"
    assert s.name == "알파"
    assert s.avg_production_time == 5.0
    assert s.yield_rate == 0.9


def test_sample_default_stock():
    s = Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9)
    assert s.stock == 0
