import os
import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository
from controller.sample_controller import SampleController

TEST_FILE = "data/test_samples_ctrl.json"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def ctrl():
    return SampleController(SampleRepository(TEST_FILE))


def test_register_sample(ctrl):
    s = ctrl.register("S-001", "알파", 5.0, 0.9)
    assert s.sample_id == "S-001"
    assert ctrl.list_all()[0].name == "알파"


def test_register_duplicate_raises(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9)
    with pytest.raises(ValueError, match="이미 존재"):
        ctrl.register("S-001", "알파2", 3.0, 0.8)


def test_list_all_empty(ctrl):
    assert ctrl.list_all() == []


def test_search_by_name(ctrl):
    ctrl.register("S-001", "알파시료", 5.0, 0.9)
    ctrl.register("S-002", "베타시료", 3.0, 0.8)
    results = ctrl.search_by_name("알파")
    assert len(results) == 1
    assert results[0].sample_id == "S-001"


def test_update_stock(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9)
    ctrl.update_stock("S-001", 100)
    assert ctrl.list_all()[0].stock == 100


def test_update_stock_not_found_raises(ctrl):
    with pytest.raises(ValueError, match="존재하지 않는"):
        ctrl.update_stock("S-999", 10)


def test_calculate_production_quantity(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9, stock=10)
    qty = ctrl.calculate_production_quantity("S-001", order_quantity=20)
    import math
    shortage = 20 - 10
    expected = math.ceil(shortage / (0.9 * 0.9))
    assert qty == expected


def test_stock_status_여유(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9, stock=50)
    assert ctrl.get_stock_status("S-001", order_quantity=30) == "여유"


def test_stock_status_부족(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9, stock=10)
    assert ctrl.get_stock_status("S-001", order_quantity=30) == "부족"


def test_stock_status_고갈(ctrl):
    ctrl.register("S-001", "알파", 5.0, 0.9, stock=0)
    assert ctrl.get_stock_status("S-001", order_quantity=30) == "고갈"
