# PRD: 데이터 영속성 처리 PoC

## 1. 개요

### 1.1 프로젝트 정보

| 항목 | 내용 |
|------|------|
| 프로젝트명 | DataPersistence PoC |
| 상위 시스템 | 반도체 시료 생산주문관리 시스템 (S-Semi) |
| PoC 목적 | 데이터 영속성 처리 방식 검증 |
| 언어 | Python 3.x |
| 아키텍처 | MVC 패턴 |

### 1.2 배경

가상의 반도체 회사 "S-Semi"는 시료(Sample) 생산주문관리 시스템을 개발하고 있다.
이 시스템은 시료 등록, 주문 접수, 생산 라인 관리, 출고 처리 등의 기능을 포함하며,
담당자가 콘솔에서 직접 명령을 입력하는 방식으로 동작한다.

기존에 엑셀과 메모장으로 주문을 관리하던 방식에서 발생하는 다음 문제를 해결하고자 한다.

- 주문 처리 여부 추적 불가
- 공정 완성 시점 파악 불가
- 재고와 공정 현황의 통합 관리 불가

본 PoC는 전체 시스템 개발 전에 **데이터 영속성(Data Persistence)** — 애플리케이션을 재시작해도 데이터를 유지하는 성질 — 구현 방식을 검증하는 것을 목적으로 한다.

---

## 2. 목표

- 시료(Sample) 및 주문(Order) 데이터를 영속적으로 저장·불러오는 구조 구현
- CRUD(Create, Read, Update, Delete) 전 연산 지원
- 애플리케이션 재시작 후에도 이전 데이터가 유지됨을 확인
- 본 PoC에서 검증된 저장 방식을 본 프로젝트(SampleOrderSystem)에 적용

---

## 3. 범위

### In Scope

- Sample 엔티티 CRUD
- Order 엔티티 CRUD
- JSON 파일 기반 저장소 구현
- Repository 패턴을 통한 저장소 추상화
- MVC 스켈레톤 구조와 연동 검증

### Out of Scope

- 전체 시스템 기능(주문 승인/거절, 생산라인, 출고 처리 등) 구현
- 사용자 인증/권한 관리
- 동시성 제어 (다중 사용자 동시 접근)
- 실시간 생산 시뮬레이션

---

## 4. 데이터 모델

### 4.1 Sample (시료)

| 필드 | 타입 | 설명 |
|------|------|------|
| `sample_id` | str | 시료 고유 ID (예: S-001) |
| `name` | str | 시료명 (예: 실리콘 웨이퍼-8인치) |
| `avg_production_time` | float | 평균 생산시간 (분/개) |
| `yield_rate` | float | 수율 (0.0 ~ 1.0, 예: 0.92) |
| `stock` | int | 현재 재고 수량 |

> 수율 = 정상적인 시료 수 / 총 생산 시료 수 (예: 100개 중 90개 정상 → 0.9)

### 4.2 Order (주문)

| 필드 | 타입 | 설명 |
|------|------|------|
| `order_id` | str | 주문 고유 번호 (예: ORD-20260416-0043) |
| `sample_id` | str | 주문한 시료 ID |
| `customer` | str | 고객명 |
| `quantity` | int | 주문 수량 |
| `status` | str | 주문 상태 (아래 참조) |
| `created_at` | str | 주문 생성 일시 (ISO 8601) |
| `updated_at` | str | 최종 상태 변경 일시 (ISO 8601) |

### 4.3 주문 상태 흐름

```
RESERVED → CONFIRMED (재고 충분)
RESERVED → PRODUCING (재고 부족, 생산라인 등록)
RESERVED → REJECTED  (거절)
PRODUCING → CONFIRMED (생산 완료)
CONFIRMED → RELEASE   (출고 완료)
```

| 상태 | 의미 |
|------|------|
| `RESERVED` | 주문 접수 |
| `REJECTED` | 주문 거절 (모니터링 제외) |
| `PRODUCING` | 승인 완료 + 재고 부족으로 생산 중 |
| `CONFIRMED` | 승인 완료 + 출고 대기 중 |
| `RELEASE` | 출고 완료 |

---

## 5. 기능 요구사항

### 5.1 저장소 구현 (Repository Layer)

#### FR-01: Sample Repository
- `create(sample)` — 새 시료 등록
- `find_by_id(sample_id)` — ID로 시료 조회
- `find_all()` — 전체 시료 목록 조회
- `find_by_name(name)` — 이름으로 시료 검색 (부분 일치)
- `update(sample)` — 시료 정보 수정 (재고 포함)
- `delete(sample_id)` — 시료 삭제

#### FR-02: Order Repository
- `create(order)` — 새 주문 생성
- `find_by_id(order_id)` — 주문 ID로 조회
- `find_all()` — 전체 주문 목록 조회
- `find_by_status(status)` — 상태별 주문 목록 조회
- `update(order)` — 주문 정보 수정 (상태 변경 포함)
- `delete(order_id)` — 주문 삭제

### 5.2 영속성 요구사항

#### FR-03: JSON 파일 저장
- 데이터는 `data/` 디렉터리 하위의 JSON 파일에 저장
  - `data/samples.json`
  - `data/orders.json`
- 애플리케이션 시작 시 파일에서 데이터를 로드
- 데이터 변경 시 즉시 파일에 반영 (write-through)
- 파일이 없을 경우 빈 초기 상태로 시작

#### FR-04: 데이터 정합성
- 존재하지 않는 `sample_id`로 주문 생성 불가
- `sample_id`는 시스템 내 유일해야 함
- `order_id`는 시스템 내 유일해야 함

### 5.3 MVC 연동 검증

#### FR-05: 콘솔 기반 검증 시나리오
다음 시나리오를 콘솔에서 실행하여 영속성을 확인한다.

1. 시료 등록 → 프로그램 재시작 → 시료 조회 (데이터 유지 확인)
2. 주문 생성 → 상태 변경 → 프로그램 재시작 → 주문 상태 확인
3. 재고 수정 → 프로그램 재시작 → 재고 확인

---

## 6. 비기능 요구사항

| 항목 | 요구사항 |
|------|----------|
| 저장 방식 | JSON 파일 (변경 가능, 추상화 인터페이스 유지) |
| 아키텍처 | MVC 패턴 — Model / Controller / View 역할 분리 |
| 코드 품질 | CleanCode 원칙 준수, 단일 책임 원칙 적용 |
| 테스트 | 각 CRUD 연산에 대한 단위 테스트 작성 |
| 확장성 | Repository 인터페이스를 통해 DB로 교체 가능한 구조 |

---

## 7. 디렉터리 구조

```
DataPersistence/
├── main.py                  # 진입점, 검증 시나리오 실행
├── model/
│   ├── sample.py            # Sample 데이터 클래스
│   └── order.py             # Order 데이터 클래스
├── repository/
│   ├── base_repository.py   # 추상 Repository 인터페이스
│   ├── sample_repository.py # Sample JSON 저장소
│   └── order_repository.py  # Order JSON 저장소
├── controller/
│   ├── sample_controller.py # 시료 비즈니스 로직
│   └── order_controller.py  # 주문 비즈니스 로직
├── view/
│   └── console_view.py      # 콘솔 출력 포맷
├── data/
│   ├── samples.json         # 시료 데이터 (자동 생성)
│   └── orders.json          # 주문 데이터 (자동 생성)
├── tests/
│   ├── test_sample_repository.py
│   └── test_order_repository.py
└── docs/
    └── PRD.md
```

---

## 8. 핵심 비즈니스 로직

### 8.1 생산량 계산

재고 부족 시 생산라인 등록에 사용되는 실 생산량 공식:

```
실 생산량 = ceil(부족분 / (수율 * 0.9))
총 생산시간 = 평균 생산시간 * 실 생산량
부족분 = 주문 수량 - 현재 재고
```

### 8.2 재고 상태 판정 (모니터링용)

| 상태 | 조건 |
|------|------|
| 여유 | 재고 >= 주문 대기 수량 |
| 부족 | 0 < 재고 < 주문 대기 수량 |
| 고갈 | 재고 == 0 |

---

## 9. 검증 완료 기준

- [ ] `samples.json`, `orders.json` 파일에 데이터가 정상 저장됨
- [ ] 프로그램 재시작 후 저장된 데이터가 정상 로드됨
- [ ] Sample CRUD 모든 연산 정상 동작
- [ ] Order CRUD 모든 연산 정상 동작
- [ ] 단위 테스트 전체 통과
- [ ] 잘못된 입력(존재하지 않는 ID 등)에 대한 오류 처리 확인
