# DataPersistence PoC

반도체 시료 생산주문관리 시스템(S-Semi)의 데이터 영속성 처리 PoC다.  
JSON 파일 기반 write-through 방식으로 `Sample`·`Order` 데이터를 저장하고, 애플리케이션 재시작 후에도 데이터가 유지됨을 검증한다.  
이 PoC를 발판으로 더 큰 시스템을 구축할 때 아키텍처와 확장 방법을 참고하라.

---

## 환경 설정

**요구사항:** Python 3.10 이상

```bash
# 가상환경 생성 및 활성화
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

---

## 빠른 시작

### 실행

```bash
python main.py
```

첫 실행 시 `data/samples.json`, `data/orders.json`이 생성되고 시료 3종과 주문 1건이 등록된다.

```
[INFO] 시료 등록: S-001 (알파시료)
[INFO] 시료 등록: S-002 (베타시료)
[INFO] 시료 등록: S-003 (감마시료)
[INFO] 주문 생성: ORD-20260508... (상태: RESERVED)
[INFO] 주문 상태 변경: ORD-20260508... → CONFIRMED
```

두 번째 실행 시 "이미 존재" 메시지가 출력되면 영속성이 정상 동작하는 것이다.

```
[INFO] 이미 존재하는 시료 ID: S-001
[INFO] 이미 존재하는 시료 ID: S-002
[INFO] 이미 존재하는 시료 ID: S-003
```

### 테스트

```bash
python -m pytest tests/ -v
```

32개 테스트가 전부 통과해야 한다.

---

## 아키텍처

```
view/               콘솔 출력 포맷만 담당. 입출력 로직 없음
  ↓
controller/         비즈니스 로직 (중복 검사, 상태 전환, 생산량 계산)
  ↓
repository/         JSON 파일 CRUD. BaseRepository 인터페이스 구현체
  ↓
model/              순수 데이터 클래스 (dataclass). 로직 없음
```

**의존성 방향은 단방향이다.** 상위 레이어가 하위 레이어에만 의존하고, 하위 레이어는 상위를 모른다.  
Controller는 `BaseRepository` 인터페이스에만 의존하므로, 저장소를 DB로 교체할 때 Repository 구현체만 바꾸면 된다.

### 각 레이어 역할

| 레이어 | 파일 | 역할 |
|---|---|---|
| `model/` | `sample.py`, `order.py` | 데이터 구조 정의 (`@dataclass`) |
| `repository/` | `base_repository.py`, `sample_repository.py`, `order_repository.py` | JSON 파일 읽기/쓰기, CRUD |
| `controller/` | `sample_controller.py`, `order_controller.py` | 비즈니스 규칙 적용 |
| `view/` | `console_view.py` | 출력 포맷 |

### 영속성 방식

write-through: `create`, `update`, `delete` 호출 즉시 JSON 파일에 반영된다.  
파일이 없으면 인스턴스 생성 시 빈 배열 `[]`로 초기화한다.

---

## 확장 가이드

### 새 도메인 엔티티 추가

`Equipment`(장비) 도메인을 추가하는 예시로 설명한다.

**Step 1 — 모델 작성** (`model/equipment.py`)

```python
from dataclasses import dataclass, field

@dataclass
class Equipment:
    equipment_id: str
    name: str
    status: str = field(default="IDLE")  # IDLE, IN_USE, MAINTENANCE
```

**Step 2 — Repository 작성** (`repository/equipment_repository.py`)

`BaseRepository`를 상속해서 5개 추상 메서드를 구현한다.  
`SampleRepository`를 그대로 복사한 뒤 `sample_id` → `equipment_id`, `Sample` → `Equipment`로 치환하면 된다.

```python
from repository.base_repository import BaseRepository
from model.equipment import Equipment
import json, os
from dataclasses import asdict

class EquipmentRepository(BaseRepository):
    def __init__(self, filepath: str = "data/equipment.json"):
        self._filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(filepath):
            self._write([])

    # _read, _write, create, find_by_id, find_all, update, delete
    # → SampleRepository와 동일한 구조, 키만 equipment_id로 변경
```

**Step 3 — Controller 작성** (`controller/equipment_controller.py`)

비즈니스 규칙이 있는 메서드만 추가한다.

```python
from model.equipment import Equipment
from repository.equipment_repository import EquipmentRepository

class EquipmentController:
    def __init__(self, repo: EquipmentRepository):
        self._repo = repo

    def register(self, equipment_id: str, name: str) -> Equipment:
        if self._repo.find_by_id(equipment_id) is not None:
            raise ValueError(f"이미 존재하는 장비 ID: {equipment_id}")
        eq = Equipment(equipment_id=equipment_id, name=name)
        self._repo.create(eq)
        return eq

    def change_status(self, equipment_id: str, status: str):
        eq = self._repo.find_by_id(equipment_id)
        if eq is None:
            raise ValueError(f"존재하지 않는 장비 ID: {equipment_id}")
        eq.status = status
        self._repo.update(eq)
```

**Step 4 — 테스트 작성** (`tests/test_equipment_repository.py`, `tests/test_equipment_controller.py`)

기존 `test_sample_repository.py`, `test_sample_controller.py`를 참고해서 같은 구조로 작성한다.  
테스트용 파일 경로는 `data/test_equipment.json`처럼 별도로 분리하고, `autouse` fixture로 테스트 후 자동 삭제한다.

---

### JSON → 데이터베이스 교체

Controller는 `BaseRepository` 인터페이스에만 의존하므로, Repository 구현체만 교체하면 Controller·View 코드는 수정 없이 그대로 동작한다.

**예시 — SQLite로 교체:**

```python
# repository/sample_repository_sqlite.py
import sqlite3
from repository.base_repository import BaseRepository
from model.sample import Sample

class SampleRepositorySQLite(BaseRepository):
    def __init__(self, db_path: str = "data/app.db"):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                sample_id TEXT PRIMARY KEY,
                name TEXT,
                avg_production_time REAL,
                yield_rate REAL,
                stock INTEGER
            )
        """)

    def create(self, entity: Sample):
        self._conn.execute(
            "INSERT INTO samples VALUES (?, ?, ?, ?, ?)",
            (entity.sample_id, entity.name, entity.avg_production_time, entity.yield_rate, entity.stock)
        )
        self._conn.commit()

    # find_by_id, find_all, update, delete 동일한 방식으로 구현
```

`main.py`에서 Repository만 교체하면 Controller는 변경 없이 동작한다.

```python
# 기존
sample_repo = SampleRepository()

# 교체 후
from repository.sample_repository_sqlite import SampleRepositorySQLite
sample_repo = SampleRepositorySQLite()
```

---

## 디렉터리 구조

```
DataPersistence/
├── main.py                        진입점 (영속성 검증 시나리오)
├── requirements.txt
├── pytest.ini
├── model/
│   ├── sample.py                  Sample 데이터 클래스
│   └── order.py                   Order 데이터 클래스
├── repository/
│   ├── base_repository.py         추상 인터페이스 (ABC)
│   ├── sample_repository.py       Sample JSON 저장소
│   └── order_repository.py        Order JSON 저장소
├── controller/
│   ├── sample_controller.py       Sample 비즈니스 로직
│   └── order_controller.py        Order 비즈니스 로직
├── view/
│   └── console_view.py            콘솔 출력 포맷
├── data/                          런타임 자동 생성 (gitignore)
│   ├── samples.json
│   └── orders.json
├── tests/
│   ├── test_sample_repository.py
│   ├── test_order_repository.py
│   ├── test_sample_controller.py
│   └── test_order_controller.py
└── docs/
    ├── PRD.md                     제품 요구사항 명세
    └── PLAN.md                    구현 태스크 계획
```
