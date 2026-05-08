# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 시료 생산주문관리 시스템(S-Semi)의 **데이터 영속성 처리 PoC**다.
애플리케이션 재시작 후에도 시료(Sample)·주문(Order) 데이터가 유지됨을 JSON 파일 기반으로 검증한다.
전체 시스템 사양은 `docs/PRD.md`, 구현 태스크별 계획은 `docs/PLAN.md`를 참조한다.

## 명령어

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 전체 테스트 실행
python -m pytest tests/ -v

# 단일 테스트 파일 실행
python -m pytest tests/test_sample_repository.py -v

# 단일 테스트 함수 실행
python -m pytest tests/test_sample_repository.py::test_create_and_find_by_id -v

# 영속성 검증 시나리오 실행
python main.py
```

## 아키텍처

MVC 패턴 + Repository 패턴의 4-레이어 구조다.

```
model/          → 순수 데이터 클래스 (dataclass). 로직 없음
repository/     → JSON 파일 CRUD. BaseRepository 인터페이스 구현체
controller/     → 비즈니스 로직 (중복 검사, 상태 전환, 생산량 계산)
view/           → 콘솔 출력 포맷만 담당. 입출력 로직 없음
data/           → samples.json, orders.json (런타임 자동 생성)
tests/          → pytest 단위 테스트
```

**의존성 방향:** `view → controller → repository → model`  
Controller는 Repository 인터페이스에만 의존하므로, 저장소를 DB로 교체할 때 Repository만 교체하면 된다.

## 핵심 도메인 규칙

**주문 상태 흐름:**
```
RESERVED → CONFIRMED   (재고 충분)
RESERVED → PRODUCING   (재고 부족 → 생산라인 등록)
RESERVED → REJECTED    (거절)
PRODUCING → CONFIRMED  (생산 완료)
CONFIRMED → RELEASE    (출고 완료)
```
`REJECTED`는 비정상 흐름으로 모니터링에서 제외한다.

**생산량 공식** (`SampleController.calculate_production_quantity`):
```
실 생산량 = ceil(부족분 / (수율 * 0.9))
부족분 = 주문 수량 − 현재 재고
```

**재고 상태 판정** (모니터링용):
- 여유: 재고 ≥ 주문 대기 수량
- 부족: 0 < 재고 < 주문 대기 수량
- 고갈: 재고 == 0

## 영속성 구현 방식

`SampleRepository`와 `OrderRepository`는 write-through 방식으로 동작한다.  
모든 쓰기 연산(`create`, `update`, `delete`) 즉시 JSON 파일에 반영된다.  
인스턴스 생성 시 파일이 없으면 빈 배열 `[]`로 초기화한다.

테스트에서는 `data/test_*.json` 별도 파일을 사용하며, `autouse` fixture로 테스트 후 자동 삭제한다.
