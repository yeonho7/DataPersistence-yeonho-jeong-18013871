# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

반도체 시료 생산주문관리 시스템(S-Semi)의 **데이터 영속성 처리 PoC**다.
애플리케이션 재시작 후에도 시료(Sample)·주문(Order) 데이터가 유지됨을 JSON 파일 기반으로 검증한다.
전체 시스템 사양은 `docs/PRD.md`, 구현 태스크별 계획은 `docs/PLAN.md`를 참조한다.

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

## 영속성 구현 방식

`SampleRepository`와 `OrderRepository`는 write-through 방식으로 동작한다.  
모든 쓰기 연산(`create`, `update`, `delete`) 즉시 JSON 파일에 반영된다.  
인스턴스 생성 시 파일이 없으면 빈 배열 `[]`로 초기화한다.

테스트에서는 `data/test_*.json` 별도 파일을 사용하며, `autouse` fixture로 테스트 후 자동 삭제한다.

## 커밋 정책

작업 단위가 완결될 때마다 즉시 커밋한다. 커밋은 최대한 자주, 작은 단위로 한다.
- 테스트 통과 → 커밋
- 기능 구현 → 커밋
- 버그 수정 → 커밋

커밋을 모아두지 않는다. 진행 상황을 항상 git 히스토리로 추적할 수 있어야 한다.
