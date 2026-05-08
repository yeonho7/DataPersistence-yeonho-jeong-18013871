import os
import pytest
from model.order import Order
from repository.order_repository import OrderRepository

TEST_FILE = "data/test_orders.json"


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


@pytest.fixture
def repo():
    return OrderRepository(TEST_FILE)


def test_order_creation():
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10)
    assert o.order_id == "ORD-001"
    assert o.sample_id == "S-001"
    assert o.customer == "고객A"
    assert o.quantity == 10


def test_order_default_status():
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10)
    assert o.status == "RESERVED"


def test_order_timestamps_auto_set():
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10)
    assert o.created_at is not None
    assert o.updated_at is not None
    assert "T" in o.created_at


def test_order_custom_status():
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10, status="CONFIRMED")
    assert o.status == "CONFIRMED"


def test_repository_create_and_find_by_id(repo):
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10)
    repo.create(o)
    found = repo.find_by_id("ORD-001")
    assert found.order_id == "ORD-001"
    assert found.customer == "고객A"


def test_repository_find_all(repo):
    repo.create(Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10))
    repo.create(Order(order_id="ORD-002", sample_id="S-002", customer="고객B", quantity=5))
    assert len(repo.find_all()) == 2


def test_repository_update(repo):
    o = Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10)
    repo.create(o)
    o.status = "CONFIRMED"
    repo.update(o)
    found = repo.find_by_id("ORD-001")
    assert found.status == "CONFIRMED"


def test_repository_delete(repo):
    repo.create(Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10))
    repo.delete("ORD-001")
    assert repo.find_by_id("ORD-001") is None


def test_repository_find_by_status(repo):
    repo.create(Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10, status="RESERVED"))
    repo.create(Order(order_id="ORD-002", sample_id="S-001", customer="고객B", quantity=5, status="CONFIRMED"))
    repo.create(Order(order_id="ORD-003", sample_id="S-002", customer="고객C", quantity=3, status="RESERVED"))
    results = repo.find_by_status("RESERVED")
    assert len(results) == 2


def test_repository_persistence_across_instances():
    repo1 = OrderRepository(TEST_FILE)
    repo1.create(Order(order_id="ORD-001", sample_id="S-001", customer="고객A", quantity=10))

    repo2 = OrderRepository(TEST_FILE)
    found = repo2.find_by_id("ORD-001")
    assert found is not None
    assert found.customer == "고객A"
