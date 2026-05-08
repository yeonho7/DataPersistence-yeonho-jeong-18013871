import os
import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.order_controller import OrderController

SAMPLE_FILE = "data/test_samples_oc.json"
ORDER_FILE = "data/test_orders_ctrl.json"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    for f in [SAMPLE_FILE, ORDER_FILE]:
        if os.path.exists(f):
            os.remove(f)


@pytest.fixture
def ctrl():
    sample_repo = SampleRepository(SAMPLE_FILE)
    sample_repo.create(Sample(sample_id="S-001", name="알파", avg_production_time=5.0, yield_rate=0.9, stock=50))
    return OrderController(OrderRepository(ORDER_FILE), sample_repo)


def test_place_order(ctrl):
    order = ctrl.place_order(sample_id="S-001", customer="고객A", quantity=10)
    assert order.sample_id == "S-001"
    assert order.status == "RESERVED"
    assert order.order_id.startswith("ORD-")


def test_place_order_invalid_sample_raises(ctrl):
    with pytest.raises(ValueError, match="존재하지 않는"):
        ctrl.place_order(sample_id="S-999", customer="고객A", quantity=10)


def test_change_status(ctrl):
    order = ctrl.place_order(sample_id="S-001", customer="고객A", quantity=10)
    ctrl.change_status(order.order_id, "CONFIRMED")
    updated = ctrl.list_all()[0]
    assert updated.status == "CONFIRMED"


def test_change_status_invalid_raises(ctrl):
    order = ctrl.place_order(sample_id="S-001", customer="고객A", quantity=10)
    with pytest.raises(ValueError, match="유효하지 않은"):
        ctrl.change_status(order.order_id, "INVALID_STATUS")


def test_change_status_not_found_raises(ctrl):
    with pytest.raises(ValueError, match="존재하지 않는"):
        ctrl.change_status("ORD-999", "CONFIRMED")


def test_list_by_status(ctrl):
    ctrl.place_order(sample_id="S-001", customer="고객A", quantity=10)
    ctrl.place_order(sample_id="S-001", customer="고객B", quantity=5)
    results = ctrl.list_by_status("RESERVED")
    assert len(results) == 2


def test_list_all(ctrl):
    ctrl.place_order(sample_id="S-001", customer="고객A", quantity=10)
    ctrl.place_order(sample_id="S-001", customer="고객B", quantity=5)
    assert len(ctrl.list_all()) == 2
