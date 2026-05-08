# DataPersistence PoC 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 반도체 시료(Sample)와 주문(Order) 데이터를 JSON 파일에 영속적으로 저장·불러오는 MVC 구조 PoC를 구현한다.

**Architecture:** Repository 패턴으로 저장소 접근을 추상화하고, Controller가 비즈니스 로직을 담당하며, View는 콘솔 출력만 처리한다. 데이터는 write-through 방식으로 `data/` 디렉터리의 JSON 파일에 즉시 반영된다.

**Tech Stack:** Python 3.x, dataclasses, json (표준 라이브러리), pytest

---

## 파일 구조

```
DataPersistence/
├── main.py
├── model/
│   ├── __init__.py
│   ├── sample.py
│   └── order.py
├── repository/
│   ├── __init__.py
│   ├── base_repository.py
│   ├── sample_repository.py
│   └── order_repository.py
├── controller/
│   ├── __init__.py
│   ├── sample_controller.py
│   └── order_controller.py
├── view/
│   ├── __init__.py
│   └── console_view.py
├── data/
│   ├── samples.json          (자동 생성)
│   └── orders.json           (자동 생성)
└── tests/
    ├── test_sample_repository.py
    ├── test_order_repository.py
    ├── test_sample_controller.py
    └── test_order_controller.py
```

---

## Task 1: 프로젝트 환경 설정

**Files:**
- Create: `requirements.txt`
- Create: `model/__init__.py`
- Create: `repository/__init__.py`
- Create: `controller/__init__.py`
- Create: `view/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: pytest 설치 확인**

```bash
python -m pytest --version
```
Expected: `pytest 7.x.x` 이상. 없으면:
```bash
pip install pytest
```

- [ ] **Step 2: requirements.txt 생성**

```
pytest>=7.0
```

- [ ] **Step 3: 패키지 `__init__.py` 파일 생성**

각 디렉터리(`model/`, `repository/`, `controller/`, `view/`, `tests/`)에 빈 `__init__.py` 파일 생성.

```bash
# Windows PowerShell
New-Item -Path model,repository,controller,view,tests -ItemType Directory -Force
foreach ($d in @("model","repository","controller","view","tests")) {
    New-Item -Path "$d\__init__.py" -ItemType File -Force
}
```

- [ ] **Step 4: pytest 실행 확인**

```bash
python -m pytest tests/ -v
```
Expected: `no tests ran` (오류 없이 종료)

- [ ] **Step 5: 커밋**

```bash
git add requirements.txt model/__init__.py repository/__init__.py controller/__init__.py view/__init__.py tests/__init__.py
git commit -m "chore: initialize project structure"
```

---

## Task 2: Sample 모델

**Files:**
- Create: `model/sample.py`
- Test: `tests/test_sample_repository.py` (일부)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_sample_repository.py`에 작성:

```python
from model.sample import Sample

def test_sample_creation():
    s = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    assert s.sample_id == "S-001"
    assert s.name == "실리콘 웨이퍼-8인치"
    assert s.avg_production_time == 0.5
    assert s.yield_rate == 0.92
    assert s.stock == 480

def test_sample_default_stock():
    s = Sample("S-002", "GaN 에피택셜", 0.3, 0.78)
    assert s.stock == 0
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_sample_repository.py::test_sample_creation -v
```
Expected: `ImportError: cannot import name 'Sample'`

- [ ] **Step 3: Sample 모델 구현**

`model/sample.py`:

```python
from dataclasses import dataclass

@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int = 0
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_sample_repository.py::test_sample_creation tests/test_sample_repository.py::test_sample_default_stock -v
```
Expected: `2 passed`

- [ ] **Step 5: 커밋**

```bash
git add model/sample.py tests/test_sample_repository.py
git commit -m "feat: add Sample model"
```

---

## Task 3: Order 모델

**Files:**
- Create: `model/order.py`
- Test: `tests/test_order_repository.py` (일부)

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_order_repository.py`에 작성:

```python
from model.order import Order

def test_order_creation():
    o = Order("ORD-20260508-0001", "S-001", "삼성전자 파운드리", 200)
    assert o.order_id == "ORD-20260508-0001"
    assert o.sample_id == "S-001"
    assert o.customer == "삼성전자 파운드리"
    assert o.quantity == 200
    assert o.status == "RESERVED"

def test_order_timestamps_auto_set():
    o = Order("ORD-001", "S-001", "고객A", 100)
    assert o.created_at != ""
    assert o.updated_at != ""

def test_order_custom_status():
    o = Order("ORD-001", "S-001", "고객A", 100, status="CONFIRMED")
    assert o.status == "CONFIRMED"
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_order_repository.py::test_order_creation -v
```
Expected: `ImportError: cannot import name 'Order'`

- [ ] **Step 3: Order 모델 구현**

`model/order.py`:

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: str = "RESERVED"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_order_repository.py::test_order_creation tests/test_order_repository.py::test_order_timestamps_auto_set tests/test_order_repository.py::test_order_custom_status -v
```
Expected: `3 passed`

- [ ] **Step 5: 커밋**

```bash
git add model/order.py tests/test_order_repository.py
git commit -m "feat: add Order model"
```

---

## Task 4: Base Repository 인터페이스

**Files:**
- Create: `repository/base_repository.py`

- [ ] **Step 1: BaseRepository 추상 클래스 작성**

`repository/base_repository.py`:

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class BaseRepository(ABC):
    @abstractmethod
    def create(self, entity):
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str):
        pass

    @abstractmethod
    def find_all(self) -> list:
        pass

    @abstractmethod
    def update(self, entity) -> bool:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass
```

- [ ] **Step 2: import 확인**

```bash
python -c "from repository.base_repository import BaseRepository; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 커밋**

```bash
git add repository/base_repository.py
git commit -m "feat: add BaseRepository interface"
```

---

## Task 5: Sample Repository (JSON 영속성)

**Files:**
- Create: `repository/sample_repository.py`
- Modify: `tests/test_sample_repository.py`

- [ ] **Step 1: CRUD 테스트 추가**

`tests/test_sample_repository.py` 하단에 추가:

```python
import os
import pytest
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

def test_create_and_find_by_id(repo):
    from model.sample import Sample
    repo.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    result = repo.find_by_id("S-001")
    assert result.name == "실리콘 웨이퍼"
    assert result.stock == 100

def test_find_all_returns_all(repo):
    from model.sample import Sample
    repo.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    repo.create(Sample("S-002", "GaN 에피택셜", 0.3, 0.78, 50))
    assert len(repo.find_all()) == 2

def test_find_by_name_partial_match(repo):
    from model.sample import Sample
    repo.create(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 100))
    repo.create(Sample("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 50))
    results = repo.find_by_name("실리콘")
    assert len(results) == 1
    assert results[0].sample_id == "S-001"

def test_update_stock(repo):
    from model.sample import Sample
    repo.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    sample = repo.find_by_id("S-001")
    sample.stock = 200
    repo.update(sample)
    assert repo.find_by_id("S-001").stock == 200

def test_delete(repo):
    from model.sample import Sample
    repo.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    repo.delete("S-001")
    assert repo.find_by_id("S-001") is None

def test_find_by_id_not_found(repo):
    assert repo.find_by_id("NOT-EXIST") is None

def test_persistence_across_instances():
    from model.sample import Sample
    repo1 = SampleRepository(TEST_FILE)
    repo1.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    repo2 = SampleRepository(TEST_FILE)
    result = repo2.find_by_id("S-001")
    assert result is not None
    assert result.name == "실리콘 웨이퍼"
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_sample_repository.py::test_create_and_find_by_id -v
```
Expected: `ImportError: cannot import name 'SampleRepository'`

- [ ] **Step 3: SampleRepository 구현**

`repository/sample_repository.py`:

```python
import json
import os
from typing import Optional, List
from model.sample import Sample
from repository.base_repository import BaseRepository

class SampleRepository(BaseRepository):
    def __init__(self, file_path: str = "data/samples.json"):
        self._file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        if not os.path.exists(self._file_path):
            self._write([])

    def _read(self) -> list:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: list):
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, sample: Sample) -> Sample:
        data = self._read()
        data.append(vars(sample))
        self._write(data)
        return sample

    def find_by_id(self, sample_id: str) -> Optional[Sample]:
        for d in self._read():
            if d["sample_id"] == sample_id:
                return Sample(**d)
        return None

    def find_all(self) -> List[Sample]:
        return [Sample(**d) for d in self._read()]

    def find_by_name(self, name: str) -> List[Sample]:
        return [Sample(**d) for d in self._read() if name.lower() in d["name"].lower()]

    def update(self, sample: Sample) -> bool:
        data = self._read()
        for i, d in enumerate(data):
            if d["sample_id"] == sample.sample_id:
                data[i] = vars(sample)
                self._write(data)
                return True
        return False

    def delete(self, sample_id: str) -> bool:
        data = self._read()
        new_data = [d for d in data if d["sample_id"] != sample_id]
        if len(new_data) == len(data):
            return False
        self._write(new_data)
        return True
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_sample_repository.py -v
```
Expected: `전체 통과` (test_sample_creation, test_sample_default_stock 포함 모두)

- [ ] **Step 5: 커밋**

```bash
git add repository/sample_repository.py tests/test_sample_repository.py
git commit -m "feat: add SampleRepository with JSON persistence"
```

---

## Task 6: Order Repository (JSON 영속성)

**Files:**
- Create: `repository/order_repository.py`
- Modify: `tests/test_order_repository.py`

- [ ] **Step 1: CRUD 테스트 추가**

`tests/test_order_repository.py` 하단에 추가:

```python
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

def test_create_and_find_by_id(repo):
    o = Order("ORD-20260508-0001", "S-001", "삼성전자", 200)
    repo.create(o)
    result = repo.find_by_id("ORD-20260508-0001")
    assert result.customer == "삼성전자"
    assert result.status == "RESERVED"

def test_find_by_status(repo):
    repo.create(Order("ORD-001", "S-001", "고객A", 100))
    repo.create(Order("ORD-002", "S-002", "고객B", 50, status="CONFIRMED"))
    reserved = repo.find_by_status("RESERVED")
    assert len(reserved) == 1
    assert reserved[0].order_id == "ORD-001"

def test_update_status(repo):
    repo.create(Order("ORD-001", "S-001", "고객A", 100))
    order = repo.find_by_id("ORD-001")
    order.status = "CONFIRMED"
    repo.update(order)
    assert repo.find_by_id("ORD-001").status == "CONFIRMED"

def test_delete(repo):
    repo.create(Order("ORD-001", "S-001", "고객A", 100))
    repo.delete("ORD-001")
    assert repo.find_by_id("ORD-001") is None

def test_find_by_id_not_found(repo):
    assert repo.find_by_id("NOT-EXIST") is None

def test_persistence_across_instances():
    repo1 = OrderRepository(TEST_FILE)
    repo1.create(Order("ORD-001", "S-001", "고객A", 100))
    repo2 = OrderRepository(TEST_FILE)
    result = repo2.find_by_id("ORD-001")
    assert result is not None
    assert result.status == "RESERVED"
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_order_repository.py::test_create_and_find_by_id -v
```
Expected: `ImportError: cannot import name 'OrderRepository'`

- [ ] **Step 3: OrderRepository 구현**

`repository/order_repository.py`:

```python
import json
import os
from typing import Optional, List
from model.order import Order
from repository.base_repository import BaseRepository

class OrderRepository(BaseRepository):
    def __init__(self, file_path: str = "data/orders.json"):
        self._file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        if not os.path.exists(self._file_path):
            self._write([])

    def _read(self) -> list:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: list):
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create(self, order: Order) -> Order:
        data = self._read()
        data.append(vars(order))
        self._write(data)
        return order

    def find_by_id(self, order_id: str) -> Optional[Order]:
        for d in self._read():
            if d["order_id"] == order_id:
                return Order(**d)
        return None

    def find_all(self) -> List[Order]:
        return [Order(**d) for d in self._read()]

    def find_by_status(self, status: str) -> List[Order]:
        return [Order(**d) for d in self._read() if d["status"] == status]

    def update(self, order: Order) -> bool:
        data = self._read()
        for i, d in enumerate(data):
            if d["order_id"] == order.order_id:
                data[i] = vars(order)
                self._write(data)
                return True
        return False

    def delete(self, order_id: str) -> bool:
        data = self._read()
        new_data = [d for d in data if d["order_id"] != order_id]
        if len(new_data) == len(data):
            return False
        self._write(new_data)
        return True
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_order_repository.py -v
```
Expected: `전체 통과`

- [ ] **Step 5: 커밋**

```bash
git add repository/order_repository.py tests/test_order_repository.py
git commit -m "feat: add OrderRepository with JSON persistence"
```

---

## Task 7: Sample Controller

**Files:**
- Create: `controller/sample_controller.py`
- Create: `tests/test_sample_controller.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_sample_controller.py`:

```python
import os
import math
import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository
from controller.sample_controller import SampleController

TEST_FILE = "data/test_ctrl_samples.json"

@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

@pytest.fixture
def ctrl():
    return SampleController(SampleRepository(TEST_FILE))

def test_register_new_sample(ctrl):
    sample = ctrl.register("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100)
    assert sample.sample_id == "S-001"
    assert sample.stock == 100

def test_register_duplicate_raises(ctrl):
    ctrl.register("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100)
    with pytest.raises(ValueError, match="already exists"):
        ctrl.register("S-001", "중복 시료", 0.5, 0.92, 0)

def test_list_all(ctrl):
    ctrl.register("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100)
    ctrl.register("S-002", "GaN 에피택셜", 0.3, 0.78, 50)
    assert len(ctrl.list_all()) == 2

def test_search_by_name(ctrl):
    ctrl.register("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 100)
    ctrl.register("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 50)
    results = ctrl.search_by_name("실리콘")
    assert len(results) == 1

def test_update_stock(ctrl):
    ctrl.register("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100)
    result = ctrl.update_stock("S-001", 50)
    assert result.stock == 150

def test_update_stock_not_found_raises(ctrl):
    with pytest.raises(ValueError, match="not found"):
        ctrl.update_stock("NOT-EXIST", 10)

def test_calculate_production_quantity(ctrl):
    qty = ctrl.calculate_production_quantity(shortage=170, yield_rate=0.92)
    assert qty == math.ceil(170 / (0.92 * 0.9))
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_sample_controller.py::test_register_new_sample -v
```
Expected: `ImportError: cannot import name 'SampleController'`

- [ ] **Step 3: SampleController 구현**

`controller/sample_controller.py`:

```python
import math
from model.sample import Sample
from repository.sample_repository import SampleRepository

class SampleController:
    def __init__(self, repo: SampleRepository):
        self._repo = repo

    def register(self, sample_id: str, name: str, avg_production_time: float,
                 yield_rate: float, stock: int = 0) -> Sample:
        if self._repo.find_by_id(sample_id):
            raise ValueError(f"Sample {sample_id} already exists")
        return self._repo.create(Sample(sample_id, name, avg_production_time, yield_rate, stock))

    def list_all(self):
        return self._repo.find_all()

    def search_by_name(self, name: str):
        return self._repo.find_by_name(name)

    def update_stock(self, sample_id: str, delta: int) -> Sample:
        sample = self._repo.find_by_id(sample_id)
        if not sample:
            raise ValueError(f"Sample {sample_id} not found")
        sample.stock += delta
        self._repo.update(sample)
        return sample

    def calculate_production_quantity(self, shortage: int, yield_rate: float) -> int:
        return math.ceil(shortage / (yield_rate * 0.9))
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_sample_controller.py -v
```
Expected: `7 passed`

- [ ] **Step 5: 커밋**

```bash
git add controller/sample_controller.py tests/test_sample_controller.py
git commit -m "feat: add SampleController"
```

---

## Task 8: Order Controller

**Files:**
- Create: `controller/order_controller.py`
- Create: `tests/test_order_controller.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_order_controller.py`:

```python
import os
import pytest
from model.sample import Sample
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.order_controller import OrderController

SAMPLE_FILE = "data/test_oc_samples.json"
ORDER_FILE = "data/test_oc_orders.json"

@pytest.fixture(autouse=True)
def cleanup():
    yield
    for f in [SAMPLE_FILE, ORDER_FILE]:
        if os.path.exists(f):
            os.remove(f)

@pytest.fixture
def ctrl():
    sample_repo = SampleRepository(SAMPLE_FILE)
    sample_repo.create(Sample("S-001", "실리콘 웨이퍼", 0.5, 0.92, 100))
    return OrderController(OrderRepository(ORDER_FILE), sample_repo)

def test_place_order_creates_reserved(ctrl):
    order = ctrl.place_order("S-001", "삼성전자", 50)
    assert order.status == "RESERVED"
    assert order.order_id.startswith("ORD-")

def test_place_order_invalid_sample_raises(ctrl):
    with pytest.raises(ValueError, match="not found"):
        ctrl.place_order("S-999", "삼성전자", 50)

def test_change_status_to_confirmed(ctrl):
    order = ctrl.place_order("S-001", "삼성전자", 50)
    updated = ctrl.change_status(order.order_id, "CONFIRMED")
    assert updated.status == "CONFIRMED"

def test_change_status_invalid_raises(ctrl):
    order = ctrl.place_order("S-001", "삼성전자", 50)
    with pytest.raises(ValueError, match="Invalid status"):
        ctrl.change_status(order.order_id, "UNKNOWN_STATUS")

def test_change_status_order_not_found_raises(ctrl):
    with pytest.raises(ValueError, match="not found"):
        ctrl.change_status("ORD-NOT-EXIST", "CONFIRMED")

def test_list_by_status(ctrl):
    ctrl.place_order("S-001", "고객A", 50)
    ctrl.place_order("S-001", "고객B", 30)
    reserved = ctrl.list_by_status("RESERVED")
    assert len(reserved) == 2

def test_list_all(ctrl):
    ctrl.place_order("S-001", "고객A", 50)
    ctrl.place_order("S-001", "고객B", 30)
    assert len(ctrl.list_all()) == 2
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
python -m pytest tests/test_order_controller.py::test_place_order_creates_reserved -v
```
Expected: `ImportError: cannot import name 'OrderController'`

- [ ] **Step 3: OrderController 구현**

`controller/order_controller.py`:

```python
from datetime import datetime
from model.order import Order
from repository.order_repository import OrderRepository
from repository.sample_repository import SampleRepository

VALID_STATUSES = {"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"}

class OrderController:
    def __init__(self, order_repo: OrderRepository, sample_repo: SampleRepository):
        self._order_repo = order_repo
        self._sample_repo = sample_repo

    def _next_order_id(self) -> str:
        date_str = datetime.now().strftime("%Y%m%d")
        orders = self._order_repo.find_all()
        seq = len([o for o in orders if date_str in o.order_id]) + 1
        return f"ORD-{date_str}-{seq:04d}"

    def place_order(self, sample_id: str, customer: str, quantity: int) -> Order:
        if not self._sample_repo.find_by_id(sample_id):
            raise ValueError(f"Sample {sample_id} not found")
        order = Order(
            order_id=self._next_order_id(),
            sample_id=sample_id,
            customer=customer,
            quantity=quantity,
        )
        return self._order_repo.create(order)

    def change_status(self, order_id: str, new_status: str) -> Order:
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        order.status = new_status
        order.updated_at = datetime.now().isoformat()
        self._order_repo.update(order)
        return order

    def list_by_status(self, status: str):
        return self._order_repo.find_by_status(status)

    def list_all(self):
        return self._order_repo.find_all()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_order_controller.py -v
```
Expected: `7 passed`

- [ ] **Step 5: 커밋**

```bash
git add controller/order_controller.py tests/test_order_controller.py
git commit -m "feat: add OrderController"
```

---

## Task 9: Console View

**Files:**
- Create: `view/console_view.py`

- [ ] **Step 1: ConsoleView 구현**

`view/console_view.py`:

```python
class ConsoleView:
    def show_samples(self, samples: list):
        print(f"\n등록 시료 목록 (총 {len(samples)}종)")
        print(f"{'ID':<10} {'시료명':<25} {'생산시간':>10} {'수율':>6} {'재고':>8}")
        print("-" * 65)
        for s in samples:
            print(f"{s.sample_id:<10} {s.name:<25} {s.avg_production_time:>7.1f}분/개"
                  f" {s.yield_rate:>6.2f} {s.stock:>6} ea")

    def show_orders(self, orders: list):
        print(f"\n주문 목록 (총 {len(orders)}건)")
        print(f"{'주문번호':<22} {'고객':<15} {'시료ID':<8} {'수량':>6} {'상태'}")
        print("-" * 65)
        for o in orders:
            print(f"{o.order_id:<22} {o.customer:<15} {o.sample_id:<8}"
                  f" {o.quantity:>6} {o.status}")

    def show_message(self, msg: str):
        print(msg)

    def show_error(self, msg: str):
        print(f"[오류] {msg}")
```

- [ ] **Step 2: import 확인**

```bash
python -c "from view.console_view import ConsoleView; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: 커밋**

```bash
git add view/console_view.py
git commit -m "feat: add ConsoleView"
```

---

## Task 10: Main 진입점 (영속성 검증 시나리오)

**Files:**
- Create: `main.py`

- [ ] **Step 1: main.py 구현**

`main.py`:

```python
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.sample_controller import SampleController
from controller.order_controller import OrderController
from view.console_view import ConsoleView


def main():
    sample_repo = SampleRepository()
    order_repo = OrderRepository()
    sample_ctrl = SampleController(sample_repo)
    order_ctrl = OrderController(order_repo, sample_repo)
    view = ConsoleView()

    print("=" * 60)
    print("  DataPersistence PoC — 영속성 검증 시나리오")
    print("=" * 60)

    # 시나리오 1: 시료 등록 (이미 존재하면 스킵)
    print("\n[시나리오 1] 시료 등록")
    for sid, name, pt, yr, stock in [
        ("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480),
        ("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220),
        ("S-003", "SiC 파워기판-6인치", 0.8, 0.92, 30),
    ]:
        try:
            s = sample_ctrl.register(sid, name, pt, yr, stock)
            view.show_message(f"  등록 완료: {s.sample_id} - {s.name}")
        except ValueError:
            view.show_message(f"  이미 존재: {sid} (스킵)")

    view.show_samples(sample_ctrl.list_all())

    # 시나리오 2: 주문 생성
    print("\n[시나리오 2] 주문 생성")
    try:
        o = order_ctrl.place_order("S-001", "삼성전자 파운드리", 200)
        view.show_message(f"  주문 완료: {o.order_id} ({o.status})")
    except ValueError as e:
        view.show_error(str(e))

    # 시나리오 3: 상태 변경
    print("\n[시나리오 3] 주문 상태 변경 (RESERVED → CONFIRMED)")
    orders = order_ctrl.list_by_status("RESERVED")
    if orders:
        updated = order_ctrl.change_status(orders[0].order_id, "CONFIRMED")
        view.show_message(f"  상태 변경 완료: {updated.order_id} → {updated.status}")

    view.show_orders(order_ctrl.list_all())

    print("\n프로그램을 재실행하면 위 데이터가 유지됩니다.")
    print("data/samples.json, data/orders.json 파일을 확인하세요.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 첫 번째 실행**

```bash
python main.py
```
Expected: 시료 3종 등록, 주문 생성, 상태 변경 메시지 출력

- [ ] **Step 3: 두 번째 실행 (영속성 확인)**

```bash
python main.py
```
Expected: `이미 존재: S-001 (스킵)` 메시지 — 재시작 후에도 데이터 유지 확인

- [ ] **Step 4: JSON 파일 확인**

```bash
python -c "import json; print(json.dumps(json.load(open('data/samples.json', encoding='utf-8')), ensure_ascii=False, indent=2))"
```
Expected: 시료 3종의 JSON 데이터 출력

- [ ] **Step 5: 전체 테스트 실행**

```bash
python -m pytest tests/ -v
```
Expected: 전체 테스트 통과 (실패 0건)

- [ ] **Step 6: 커밋**

```bash
git add main.py
git commit -m "feat: add main entry point and verify persistence scenarios"
```

---

## 검증 체크리스트

- [ ] `data/samples.json`, `data/orders.json` 파일에 데이터 저장 확인
- [ ] `python main.py` 재실행 시 "이미 존재" 메시지 — 영속성 확인
- [ ] `python -m pytest tests/ -v` 전체 통과
- [ ] 존재하지 않는 ID 입력 시 `ValueError` 발생 확인
- [ ] 잘못된 주문 상태 입력 시 `ValueError` 발생 확인
