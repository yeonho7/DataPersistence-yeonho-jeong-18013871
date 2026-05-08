import pytest
from model.order import Order


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
