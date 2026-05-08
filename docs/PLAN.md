# DataPersistence PoC 구현 계획

**Goal:** 반도체 시료(Sample)와 주문(Order) 데이터를 JSON 파일에 영속적으로 저장·불러오는 MVC 구조 PoC를 구현한다.

**Architecture:** Repository 패턴으로 저장소 접근을 추상화하고, Controller가 비즈니스 로직을 담당하며, View는 콘솔 출력만 처리한다. 데이터는 write-through 방식으로 `data/` 디렉터리의 JSON 파일에 즉시 반영된다.

**Tech Stack:** Python 3.x, dataclasses, json (표준 라이브러리), pytest

---

## 파일 구조

```
DataPersistence/
├── main.py
├── pytest.ini
├── requirements.txt
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

- [ ] **Step 1: requirements.txt 생성** — `pytest>=7.0` 기재
- [ ] **Step 2: 패키지 `__init__.py` 파일 생성** — 각 디렉터리에 빈 파일 생성
- [ ] **Step 3: 커밋**

---

## Task 2: Sample 모델

**Files:**
- Create: `model/sample.py`
- Test: `tests/test_sample_repository.py` (일부)

**모델 필드:** `sample_id`, `name`, `avg_production_time`, `yield_rate`, `stock` (기본값 0)

- [ ] **Step 1: 실패하는 테스트 작성** — `test_sample_creation`, `test_sample_default_stock`
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: Sample 모델 구현** — `@dataclass` 사용
- [ ] **Step 4: 테스트 통과 확인**
- [ ] **Step 5: 커밋**

---

## Task 3: Order 모델

**Files:**
- Create: `model/order.py`
- Test: `tests/test_order_repository.py` (일부)

**모델 필드:** `order_id`, `sample_id`, `customer`, `quantity`, `status` (기본값 `RESERVED`), `created_at`, `updated_at` (`__post_init__`에서 자동 설정)

- [ ] **Step 1: 실패하는 테스트 작성** — `test_order_creation`, `test_order_timestamps_auto_set`, `test_order_custom_status`
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: Order 모델 구현** — `@dataclass` + `__post_init__`으로 타임스탬프 자동 설정
- [ ] **Step 4: 테스트 통과 확인**
- [ ] **Step 5: 커밋**

---

## Task 4: Base Repository 인터페이스

**Files:**
- Create: `repository/base_repository.py`

**추상 메서드:** `create`, `find_by_id`, `find_all`, `update`, `delete`

- [ ] **Step 1: BaseRepository 추상 클래스 작성** — `ABC` + `@abstractmethod` 사용
- [ ] **Step 2: import 확인**
- [ ] **Step 3: 커밋**

---

## Task 5: Sample Repository (JSON 영속성)

**Files:**
- Create: `repository/sample_repository.py`
- Modify: `tests/test_sample_repository.py`

**구현 사항:** `BaseRepository` 구현체. 생성 시 파일 없으면 빈 배열로 초기화. 추가 메서드: `find_by_name` (부분 일치)

**테스트 커버리지:** create/find/update/delete CRUD, `find_by_name` 부분 일치, 인스턴스 간 영속성 확인

- [ ] **Step 1: CRUD 테스트 추가** — `autouse` fixture로 테스트 후 `data/test_samples.json` 자동 삭제
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: SampleRepository 구현** — write-through, `data/samples.json` 기본 경로
- [ ] **Step 4: 테스트 통과 확인**
- [ ] **Step 5: 커밋**

---

## Task 6: Order Repository (JSON 영속성)

**Files:**
- Create: `repository/order_repository.py`
- Modify: `tests/test_order_repository.py`

**구현 사항:** `BaseRepository` 구현체. 추가 메서드: `find_by_status`

**테스트 커버리지:** create/find/update/delete CRUD, `find_by_status` 필터링, 인스턴스 간 영속성 확인

- [ ] **Step 1: CRUD 테스트 추가** — `autouse` fixture로 테스트 후 `data/test_orders.json` 자동 삭제
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: OrderRepository 구현** — write-through, `data/orders.json` 기본 경로
- [ ] **Step 4: 테스트 통과 확인**
- [ ] **Step 5: 커밋**

---

## Task 7: Sample Controller

**Files:**
- Create: `controller/sample_controller.py`
- Create: `tests/test_sample_controller.py`

**구현 사항:** `register` (중복 시 ValueError), `list_all`, `search_by_name`, `update_stock` (존재하지 않는 ID 시 ValueError), `calculate_production_quantity` (부족량 / (수율 × 0.9), 올림)

- [ ] **Step 1: 실패하는 테스트 작성** — 7개 케이스 (정상/에러 분기 포함)
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: SampleController 구현**
- [ ] **Step 4: 테스트 통과 확인 (7 passed)**
- [ ] **Step 5: 커밋**

---

## Task 8: Order Controller

**Files:**
- Create: `controller/order_controller.py`
- Create: `tests/test_order_controller.py`

**구현 사항:** `place_order` (존재하지 않는 sample_id 시 ValueError, order_id 자동 생성), `change_status` (유효하지 않은 상태·존재하지 않는 order_id 시 ValueError), `list_by_status`, `list_all`

**유효 상태:** `RESERVED`, `REJECTED`, `PRODUCING`, `CONFIRMED`, `RELEASE`

- [ ] **Step 1: 실패하는 테스트 작성** — 7개 케이스 (정상/에러 분기 포함)
- [ ] **Step 2: 테스트 실패 확인**
- [ ] **Step 3: OrderController 구현**
- [ ] **Step 4: 테스트 통과 확인 (7 passed)**
- [ ] **Step 5: 커밋**

---

## Task 9: Console View

**Files:**
- Create: `view/console_view.py`

**구현 사항:** `show_samples`, `show_orders`, `show_message`, `show_error` — 출력 포맷만 담당, 입출력 로직 없음

- [ ] **Step 1: ConsoleView 구현**
- [ ] **Step 2: import 확인**
- [ ] **Step 3: 커밋**

---

## Task 10: Main 진입점 (영속성 검증 시나리오)

**Files:**
- Create: `main.py`

**시나리오:**
1. 시료 3종 등록 (이미 존재하면 스킵)
2. 주문 생성 (S-001, RESERVED)
3. 주문 상태 변경 (RESERVED → CONFIRMED)

- [ ] **Step 1: main.py 구현**
- [ ] **Step 2: 첫 번째 실행** — 시료 3종 등록, 주문 생성, 상태 변경 확인
- [ ] **Step 3: 두 번째 실행** — "이미 존재" 메시지로 영속성 확인
- [ ] **Step 4: JSON 파일 확인** — `data/samples.json` 내용 검증
- [ ] **Step 5: 전체 테스트 실행** — `python -m pytest tests/ -v` 전체 통과
- [ ] **Step 6: 커밋**

---

## 검증 체크리스트

- [ ] `data/samples.json`, `data/orders.json` 파일에 데이터 저장 확인
- [ ] `python main.py` 재실행 시 "이미 존재" 메시지 — 영속성 확인
- [ ] `python -m pytest tests/ -v` 전체 통과
- [ ] 존재하지 않는 ID 입력 시 `ValueError` 발생 확인
- [ ] 잘못된 주문 상태 입력 시 `ValueError` 발생 확인
