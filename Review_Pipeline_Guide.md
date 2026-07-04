# 코드 리뷰 파이프라인 가이드

## 메타데이터

| 항목 | 내용 |
|------|------|
| **버전** | 1.1.0 |
| **최종 업데이트** | 2026-01-26 |
| **참조 문서** | `research/classification.md`, `research/backend_cleancode.md` |
| **언어** | 한국어 |
| **용도** | Claude AI 코드 리뷰 수행 가이드 |

---

## 1. Quick Start (빠른 시작)

코드 리뷰 수행 시 아래 4단계 플로우를 순차적으로 실행합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│  [1. CLASSIFY]  →  [2. DEPTH]  →  [3. REVIEW]  →  [4. OUTPUT]  │
│     PR 분류         리뷰 깊이       체크리스트       표준 형식   │
│                      결정           기반 리뷰         출력       │
└─────────────────────────────────────────────────────────────────┘
```

### 1.1 단계별 요약

| 단계 | 작업 | 핵심 질문 |
|------|------|-----------|
| **CLASSIFY** | 위험도, 규모, 도메인, 변경 유형 분류 | "이 변경은 어떤 성격인가?" |
| **DEPTH** | 리뷰 Tier 결정 (1~4) | "얼마나 깊이 리뷰해야 하는가?" |
| **REVIEW** | Tier별 + 변경 유형별 체크리스트 적용 | "무엇을 확인해야 하는가?" |
| **OUTPUT** | 표준 형식으로 결과 출력 | "어떻게 결과를 전달할 것인가?" |

---

## 2. 분류 체계 (Classification System)

PR을 다음 5가지 축으로 분류합니다.

### 2.1 위험도 분류 (Risk Level)

> **참조**: [R002-S2.1] 위험 기반 우선순위화

| Level | 기준 | 예시 | 리뷰 요구사항 |
|-------|------|------|---------------|
| **CRITICAL** | 보안, 인증, 결제, 규제 준수 영역 | 인증 로직 변경, 결제 처리, 암호화 모듈, PII 처리 | 시니어 2인 + 보안/컴플라이언스팀 |
| **HIGH** | 아키텍처, 핵심 도메인, 데이터 무결성 | 핵심 비즈니스 로직, DB 스키마, API 계약 변경 | 시니어 2인 이상 |
| **MEDIUM** | 일반 기능, 제한된 영향 범위 | 단일 모듈 기능 추가/수정, 일반 버그 수정 | 표준 1인 리뷰 |
| **LOW** | 비기능적 변경, 시스템 영향 미미 | 문서, 주석, 오타 수정, 단순 스타일 변경 | 경량 리뷰 또는 자동 승인 |

### 2.2 변경 규모 분류 (Change Size)

> **참조**: [R002-S2.3] PR 크기와 복잡도

| Size | LOC (Lines of Code) | 처리 방식 |
|------|---------------------|-----------|
| **XS** | ~50줄 | 신속 리뷰 (Fast Track) |
| **S** | 51~100줄 | 표준 리뷰 |
| **M** | 101~200줄 | 심층 리뷰 |
| **L** | 201~500줄 | 분할 권고, 추가 컨텍스트 필요 |
| **XL** | 500줄+ | **분할 필수**, 단계별 리뷰 또는 설계 검토 선행 |

**권장사항**: Google 기준 약 200줄 이하를 "작은 변경"으로 간주. 대규모 변경은 여러 PR로 분할하는 것이 리뷰 품질 향상에 효과적.

### 2.3 도메인 분류 (Domain Type) - DDD 기반

> **참조**: [R001-S3.1], [R002-S3.1] 핵심 도메인 vs 지원/범용 도메인

| 도메인 | 정의 | 비중 | 리뷰 초점 |
|--------|------|------|-----------|
| **Core** | 비즈니스 경쟁우위를 결정짓는 핵심 영역 | ~5% | 도메인 전문가 필수, 비즈니스 로직 정확성, 최고 수준 테스트 요구 |
| **Supporting** | 핵심을 지원하는 부수 기능 | ~25% | 통합성 검토, 핵심과의 경계 분리 확인 |
| **Generic** | 범용 기능, 대체 가능한 영역 | ~70% | 모범사례 준수, 표준 호환성, 외부 의존성 관리 |

**Core 도메인 식별 질문**:
- 이 기능이 없으면 비즈니스가 성립하지 않는가?
- 이 부분이 경쟁사와 차별화되는 핵심인가?
- 외부 솔루션으로 대체할 수 없는가?

### 2.4 변경 유형 분류 (Change Type) - IEEE/ISO 14764 기반

> **참조**: [R001-S4.1], [R002-S4.1] 소프트웨어 변경 유형

| 유형 | 정의 | 리뷰 중점 |
|------|------|-----------|
| **Corrective** | 결함/버그 수정 | 회귀 테스트, 근본 원인 해결 여부, 재현 테스트 포함 확인 |
| **Adaptive** | 환경 변화 대응 (OS, API, 라이브러리 등) | 호환성, 구성 파일 유효성, 마이그레이션 전략 |
| **Perfective** | 기능 개선, 성능 향상 | 요구사항 충족, 성능 테스트 결과, 사용성 개선 |
| **Preventive** | 리팩토링, 예방적 개선 | 복잡도 감소 확인, 기존 동작 유지, 테스트 커버리지 |

### 2.5 규제/보안 민감도 분류 (Sensitivity)

> **참조**: [R001-S3.2], [R002-S3.2] 규제 및 보안 민감도

| 규제 | 적용 영역 | 추가 요구사항 |
|------|-----------|---------------|
| **SOX** | 재무, 회계, 감사 관련 | 2인 승인 필수, 7년간 로그 보관, 직무 분리 |
| **PCI-DSS** | 결제, 카드 정보 처리 | 보안팀 리뷰, OWASP Top 10 검사, 취약점 스캔 |
| **HIPAA** | 의료 정보 (PHI) 처리 | 프라이버시팀 리뷰, 암호화 확인, 6년간 기록 보관 |
| **GDPR** | 개인정보 (PII) 처리 | 법무팀 검토, 데이터 삭제/마스킹 로직 확인 |
| **NONE** | 규제 미해당 | 표준 절차 적용 |

---

## 3. 리뷰 깊이 매트릭스 (Review Depth Matrix)

### 3.1 Tier 결정 로직

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Tier 결정 Decision Tree                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  START                                                              │
│    │                                                                │
│    ▼                                                                │
│  Risk == CRITICAL  ──YES──►  TIER 1 (Full Deep)                    │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  Sensitivity != NONE  ──YES──►  TIER 1 (Full Deep)                 │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  Risk == HIGH  ──YES──►  TIER 2 (Comprehensive)                    │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  Size >= L (201줄+)  ──YES──►  TIER 2 (Comprehensive)              │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  Risk == MEDIUM  ──YES──►  TIER 3 (Standard)                       │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  Size == M (101~200줄)  ──YES──►  TIER 3 (Standard)                │
│    │                                                                │
│    NO                                                               │
│    │                                                                │
│    ▼                                                                │
│  TIER 4 (Light)                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Tier별 리뷰 요구사항

| Tier | 깊이 | 리뷰어 구성 | 예상 소요 | 주요 활동 |
|------|------|-------------|-----------|-----------|
| **TIER 1** | Full Deep | 시니어 2인 + 전문팀 (보안/컴플라이언스) | 1~2일 | 전체 코드 라인별 검토, 아키텍처 영향 분석, 보안 취약점 심층 검사, 롤백 계획 확인 |
| **TIER 2** | Comprehensive | 시니어 1인 + 도메인 전문가 | 4~8시간 | 비즈니스 로직 검증, 테스트 커버리지 확인, 성능 영향 분석 |
| **TIER 3** | Standard | 1인 리뷰 (팀 동료) | 1~4시간 | 기능 동작 확인, 코드 품질, 스타일 준수 |
| **TIER 4** | Light | 자동화 체크 + 간략 확인 | 30분 이내 | 빌드 통과, 기본 테스트, CI 검사 결과 확인 |

---

## 4. 리뷰 체크리스트 (Review Checklists)

### 4.1 공통 체크리스트 (모든 Tier 적용)

```markdown
## 공통 검증 항목
- [ ] 빌드 성공 여부
- [ ] 기존 테스트 통과
- [ ] 명백한 보안 취약점 없음 (하드코딩된 시크릿, SQL 인젝션 등)
- [ ] 코딩 스타일/컨벤션 준수
- [ ] 린트/정적 분석 통과
```

### 4.2 Tier별 추가 체크리스트

#### TIER 1 (Full Deep)

```markdown
## 보안/컴플라이언스 검토
- [ ] 인증/인가 로직 정확성
- [ ] 암호화 적용 여부 (at-rest, in-transit)
- [ ] 민감 데이터 노출 위험
- [ ] 규제 요구사항 충족 (SOX/PCI/HIPAA/GDPR)
- [ ] 감사 로그 적절성

## 아키텍처 검토
- [ ] 시스템 설계 원칙 준수
- [ ] 확장성/성능 영향
- [ ] 다른 서비스와의 의존성 변화
- [ ] API 계약 변경 여부 및 하위 호환성

## 운영 검토
- [ ] 롤백 계획 수립
- [ ] 배포 전략 (Blue-Green, Canary 등)
- [ ] 모니터링/알림 설정
- [ ] 장애 시나리오 대응 방안
```

#### TIER 2 (Comprehensive)

```markdown
## 비즈니스 로직 검토
- [ ] 요구사항/스토리 충족
- [ ] 엣지 케이스 처리
- [ ] 에러 핸들링 적절성
- [ ] 트랜잭션 일관성

## 테스트 검토
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 커버리지
- [ ] 테스트 케이스 충분성
- [ ] 회귀 테스트 통과

## 성능 검토
- [ ] 쿼리 최적화
- [ ] N+1 문제 없음
- [ ] 메모리/리소스 사용 적절성
```

#### TIER 3 (Standard)

```markdown
## 기능 검토
- [ ] 기능 동작 정상
- [ ] UI/UX 일관성 (해당 시)
- [ ] 로깅 적절성

## 코드 품질
- [ ] 코드 가독성
- [ ] 중복 코드 최소화
- [ ] 적절한 네이밍
- [ ] 주석 필요성/적절성
```

#### TIER 4 (Light)

```markdown
## 기본 검증
- [ ] CI 파이프라인 통과
- [ ] 명백한 오류 없음
- [ ] 변경 범위가 설명과 일치
```

### 4.3 변경 유형별 추가 체크리스트

#### Corrective (버그 수정)

```markdown
## 버그 수정 검증
- [ ] 원인 분석 (Root Cause) 문서화
- [ ] 재현 테스트 케이스 포함
- [ ] 회귀 방지 테스트 추가
- [ ] 유사 버그 다른 위치 점검
- [ ] 부작용(Side Effect) 없음 확인
```

#### Perfective (기능 개선)

```markdown
## 기능 개선 검증
- [ ] 요구사항 추적 (티켓/스토리 연결)
- [ ] 수락 기준 충족
- [ ] 사용자 문서/가이드 업데이트
- [ ] 기능 플래그 적용 (필요 시)
```

#### Adaptive (환경 대응)

```markdown
## 환경 적응 검증
- [ ] 호환성 매트릭스 확인
- [ ] 마이그레이션 스크립트/절차
- [ ] 롤백 절차 수립
- [ ] 의존성 버전 명시
```

#### Preventive (리팩토링)

```markdown
## 리팩토링 검증
- [ ] 기존 동작 유지 (behavior preservation)
- [ ] 복잡도 메트릭 개선 확인
- [ ] 테스트 커버리지 유지/증가
- [ ] 성능 저하 없음
```

---

## 5. 출력 형식 표준 (Output Format Standards)

### 5.1 Review Summary Template

```markdown
## Code Review Summary

### Classification
| 항목 | 값 |
|------|-----|
| **Risk Level** | [CRITICAL / HIGH / MEDIUM / LOW] |
| **Change Size** | [XS / S / M / L / XL] (약 N줄) |
| **Domain Type** | [Core / Supporting / Generic] |
| **Change Type** | [Corrective / Adaptive / Perfective / Preventive] |
| **Sensitivity** | [SOX / PCI-DSS / HIPAA / GDPR / NONE] |
| **Review Tier** | [TIER 1 / TIER 2 / TIER 3 / TIER 4] |

### Overall Assessment
**[APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION]**

[전체 평가 요약 1~2문장]

### Findings Summary
| Severity | Count | Categories |
|----------|-------|------------|
| Critical | N | [카테고리 나열] |
| High | N | [카테고리 나열] |
| Medium | N | [카테고리 나열] |
| Low | N | [카테고리 나열] |
| Info | N | [카테고리 나열] |

### Detailed Findings
[개별 Finding 상세]

### Recommendations
[전체 권고사항]
```

### 5.2 Finding Format

```markdown
### Finding #N
**Severity:** [CRITICAL / HIGH / MEDIUM / LOW / INFO]
**Category:** [Security / Logic / Performance / Reliability / Maintainability / Testing / Documentation / Style]
**Location:** `path/to/file.ext:line_number`

**Issue:**
[문제점에 대한 명확한 설명]

**Recommendation:**
[구체적인 해결 방안 또는 개선 제안]

**Code Example (선택):**
```[language]
// Before
[문제 코드]

// After (권장)
[개선 코드]
```
```

### 5.3 Severity 정의

| Level | 정의 | 조치 | 머지 영향 |
|-------|------|------|-----------|
| **CRITICAL** | 즉시 수정 필수. 보안 취약점, 데이터 손실, 시스템 장애 유발 가능 | 머지 전 반드시 해결 | **머지 차단** |
| **HIGH** | 기능 오동작, 성능 심각 저하, 중요 요구사항 미충족 | 머지 전 수정 강력 권고 | 머지 차단 권고 |
| **MEDIUM** | 잠재적 문제, 모범 사례 미준수, 경미한 버그 | 이번 PR 또는 다음 PR에서 해결 | 조건부 승인 가능 |
| **LOW** | 사소한 개선점, 코드 스타일, 가독성 향상 | 선택적 적용 | 승인에 영향 없음 |
| **INFO** | 참고 사항, 제안, 칭찬, 학습 포인트 | 조치 불필요 | 승인에 영향 없음 |

### 5.4 Category 분류

| Category | 설명 | 예시 |
|----------|------|------|
| **Security** | 보안 취약점, 인증/인가, 암호화 | XSS, SQL Injection, 하드코딩된 시크릿 |
| **Logic** | 비즈니스 로직 오류, 알고리즘 문제 | 잘못된 조건문, 경계값 오류, 무한 루프 |
| **Performance** | 성능 저하 요인 | N+1 쿼리, 불필요한 반복, 메모리 누수 |
| **Reliability** | 안정성, 에러 핸들링 | 예외 미처리, 널 체크 누락, 리소스 미해제 |
| **Maintainability** | 유지보수성, 코드 구조 | 복잡도 과다, 중복 코드, 긴 함수 |
| **Testing** | 테스트 관련 | 테스트 누락, 불충분한 커버리지, 깨진 테스트 |
| **Documentation** | 문서화 | 주석 부족, API 문서 미비, README 미업데이트 |
| **Style** | 코딩 스타일, 컨벤션 | 네이밍, 포맷팅, 불일치 스타일 |

---

## 6. 리서치 참조 체계 (Research Reference System)

### 6.1 Research Index

| ID | 문서 | 주요 내용 |
|----|------|-----------|
| **R001** | `research/classification.md` | 분류 체계, 다중 파이프라인, 통합 트리아지 |
| **R002** | `research/backend_cleancode.md` | 위험 기반 분류, 산업계 베스트 프랙티스 |

### 6.2 Citation 형식

```
[R001-S2.1] = classification.md의 Section 2.1
[R002-S3.2] = backend_cleancode.md의 Section 3.2
```

### 6.3 주요 참조 매핑

| 분류 축 | 참조 |
|---------|------|
| 위험도 기반 분류 | [R002-S2.1] |
| 도메인 기반 분류 | [R001-S3.1], [R002-S3.1] |
| 변경 유형 분류 | [R001-S4.1], [R002-S4.1] |
| 복잡도 기반 분류 | [R001-S5.1], [R001-S5.2] |
| 규제/보안 분류 | [R001-S3.2], [R002-S3.2] |
| 통합 파이프라인 | [R001-S6], [R002-S6] |

---

## 7. 에스컬레이션 경로 (Escalation Paths)

### 7.1 기본 원칙

> **불확실하면 높은 Tier로 기본 설정**

분류가 명확하지 않거나 판단이 어려운 경우, 항상 더 높은 위험도/Tier로 분류하여 안전한 방향으로 처리합니다.

### 7.2 에스컬레이션 시나리오

| 상황 | 조치 |
|------|------|
| **분류 불명확** | 높은 Tier로 기본 설정, 시니어 개발자에게 분류 확인 요청 |
| **도메인 전문지식 필요** | 해당 도메인 전문가 태그/멘션 |
| **규제/법적 판단 필요** | 컴플라이언스팀 또는 법무팀 검토 요청 |
| **보안 우려** | 보안팀 즉시 리뷰 요청 |
| **아키텍처 영향 큼** | 아키텍트/테크 리드 검토 필수 |
| **성능 영향 우려** | SRE/Platform 팀 검토 |
| **리뷰어 간 의견 충돌** | 테크 리드 또는 아키텍트 중재 |

### 7.3 연락처 (템플릿)

```markdown
## 에스컬레이션 연락처

| 영역 | 담당 | 연락 방법 |
|------|------|-----------|
| 보안 | @security-team | #security-reviews 채널 |
| 컴플라이언스 | @compliance-team | #compliance 채널 |
| 아키텍처 | @architects | #architecture-review 채널 |
| SRE/운영 | @sre-team | #sre-support 채널 |

※ 조직에 맞게 수정하여 사용
```

---

## 8. 부록

### 8.1 복잡도 지표 참고

> **참조**: [R001-S5.1], [R001-S5.2]

#### 순환 복잡도 (Cyclomatic Complexity)
- 15 초과: 이해 어려움
- 30 초과: 극도로 복잡함, 리팩토링 필요

#### 인지 복잡도 (Cognitive Complexity)
- 코드 중첩, 논리 구성의 난해함 반영
- 높을수록 리뷰어에게 더 많은 시간/경험 필요

#### 결합도 (Coupling)
- **Afferent Coupling (Ca)**: 외부에서 참조하는 수 (높으면 변경 영향 큼)
- **Efferent Coupling (Ce)**: 외부에 의존하는 수

### 8.2 리뷰 품질 지표

| 지표 | 권장 기준 |
|------|-----------|
| PR 크기 | 200줄 이하 (Google 기준) |
| 리뷰 완료 시간 | 4시간 이내 (Google 평균) |
| 초기 피드백 시간 | 1시간 이내 |
| 리뷰어 수 | 1~2인 (대부분의 경우) |

### 8.3 자동화 연계 포인트

본 가이드는 순수 가이드 문서로 유지되며, 아래 영역에서 자동화와 연계할 수 있습니다:

- **CODEOWNERS**: 경로 기반 리뷰어 자동 할당
- **PR 템플릿**: 변경 유형/규제 체크박스
- **CI/CD**: 빌드, 테스트, 린트, 보안 스캔 자동 실행
- **라벨링**: 위험도/Tier 자동 라벨 부착
- **Branch Protection**: Tier별 승인 규칙 적용

### 8.4 정량적 복잡도 기준

#### 순환 복잡도 (Cyclomatic Complexity) 기준

| CC 범위 | 위험 등급 | 리뷰 권고 |
|---------|-----------|-----------|
| **1-10** | LOW | 표준 리뷰 |
| **11-15** | MEDIUM | 주의 리뷰, 복잡도 개선 권고 |
| **16-25** | HIGH | 심층 리뷰, 리팩토링 권고 |
| **26+** | CRITICAL | 리팩토링 필수, 분할 필요 |

#### 인지 복잡도 (Cognitive Complexity) 기준

| CogC 범위 | 위험 등급 | 조치 |
|-----------|-----------|------|
| **0-10** | LOW | 양호 |
| **11-20** | MEDIUM | 개선 고려 |
| **21-30** | HIGH | 개선 권고 |
| **31+** | CRITICAL | 즉시 개선 필요 |

#### 결합도 기준

| 지표 | 권장 범위 | 경고 수준 |
|------|-----------|-----------|
| **Afferent Coupling (Ca)** | 0-10 | 20+ 시 변경 영향도 검토 필수 |
| **Efferent Coupling (Ce)** | 0-10 | 15+ 시 의존성 검토 필요 |
| **Instability (Ce/(Ca+Ce))** | 0.3-0.7 | 0, 1에 가까우면 설계 검토 |

---

## 9. 자동 분류 기준 (Auto-Classification Criteria)

### 9.1 Risk Level 자동 판단

#### 경로 패턴 기반 분류

| Risk Level | 경로 패턴 (정규식) |
|------------|-------------------|
| **CRITICAL** | `auth/`, `security/`, `payment/`, `crypto/`, `pii/`, `secret/`, `credential/` |
| **HIGH** | `core/`, `domain/`, `api/`, `db/`, `schema/`, `migration/`, `transaction/` |
| **MEDIUM** | `feature/`, `service/`, `handler/`, `controller/`, `repository/` |
| **LOW** | `docs/`, `test/`, `spec/`, `config/`, `readme`, `.md`, `mock/` |

#### 키워드 기반 분류

| Risk Level | 코드/커밋 키워드 |
|------------|-----------------|
| **CRITICAL** | `password`, `token`, `secret`, `encrypt`, `decrypt`, `apikey`, `credential`, `private_key`, `certificate` |
| **HIGH** | `transaction`, `migration`, `contract`, `interface`, `schema`, `breaking_change` |
| **MEDIUM** | `feature`, `add`, `update`, `modify` |
| **LOW** | `doc`, `comment`, `typo`, `style`, `format`, `readme` |

### 9.2 Change Type 자동 판단

#### 커밋 메시지/PR 제목 키워드

| Change Type | 키워드 패턴 |
|-------------|------------|
| **Corrective** | `fix`, `bug`, `hotfix`, `patch`, `resolve`, `issue`, `error`, `defect`, `crash` |
| **Adaptive** | `upgrade`, `migrate`, `update dependency`, `version`, `compatibility`, `bump`, `renovate` |
| **Perfective** | `feat`, `feature`, `add`, `implement`, `enhance`, `improve`, `optimize`, `perf` |
| **Preventive** | `refactor`, `restructure`, `cleanup`, `tech debt`, `reorganize`, `chore`, `rename` |

### 9.3 Sensitivity 자동 판단

#### 규제별 경로/키워드

| Sensitivity | 경로 패턴 | 키워드 |
|-------------|-----------|--------|
| **SOX** | `finance/`, `audit/`, `accounting/`, `journal/` | `audit`, `financial`, `accounting`, `ledger`, `fiscal` |
| **PCI-DSS** | `payment/`, `checkout/`, `billing/`, `card/` | `card`, `payment`, `pan`, `cvv`, `checkout`, `stripe`, `paypal` |
| **HIPAA** | `health/`, `medical/`, `patient/`, `clinical/` | `patient`, `medical`, `health`, `phi`, `diagnosis`, `prescription` |
| **GDPR** | `user/`, `privacy/`, `consent/`, `personal/` | `personal`, `pii`, `consent`, `user_data`, `privacy`, `gdpr`, `data_subject` |

### 9.4 Domain 자동 판단

#### 경로 기반 힌트

| Domain | 경로 패턴 예시 |
|--------|---------------|
| **Core** | `domain/`, `core/`, `business/`, `{product-specific-name}/` |
| **Supporting** | `service/`, `adapter/`, `integration/`, `notification/`, `email/`, `sms/` |
| **Generic** | `util/`, `utils/`, `common/`, `lib/`, `helper/`, `infrastructure/`, `shared/` |

#### 판단 보조 질문 (자동화 불가 시 수동 확인)

1. 이 코드가 없으면 비즈니스가 성립 불가능한가? → **Core**
2. 핵심 기능을 직접 지원하는가? → **Supporting**
3. 범용적이며 외부 라이브러리로 대체 가능한가? → **Generic**

---

## 10. 완성도 평가 기준 (Completeness Evaluation Criteria)

### 10.1 영역별 점수 산정 기준

#### 기능 완성도 (25점 만점)

| 점수 | 기준 |
|------|------|
| **25** | 모든 요구사항 완벽 충족, 엣지 케이스 처리 완료 |
| **20** | 핵심 요구사항 충족, 일부 엣지 케이스 미처리 |
| **15** | 주요 기능 동작, 일부 시나리오 미완성 |
| **10** | 기본 기능만 동작, 상당 부분 미완성 |
| **5** | 기능 불완전, 주요 시나리오 실패 |
| **0** | 기능 미동작 |

#### 코드 품질 (25점 만점)

| 점수 | 기준 |
|------|------|
| **25** | 클린 코드, 적절한 추상화, 높은 가독성, SOLID 준수 |
| **20** | 전반적으로 양호, 사소한 개선점 존재 |
| **15** | 평균 수준, MEDIUM 이하 품질 이슈 존재 |
| **10** | 가독성/유지보수성 문제 다수 |
| **5** | 심각한 코드 스멜, 복잡도 과다 |
| **0** | 이해 불가능한 코드 |

#### 테스트 커버리지 (25점 만점)

| 점수 | 기준 |
|------|------|
| **25** | 커버리지 80%+, 핵심 경로 및 엣지 케이스 테스트 완료 |
| **20** | 커버리지 60-79%, 주요 경로 테스트 완료 |
| **15** | 커버리지 40-59%, 기본 테스트 존재 |
| **10** | 커버리지 20-39%, 테스트 부족 |
| **5** | 커버리지 20% 미만, 최소 테스트만 존재 |
| **0** | 테스트 없음 또는 테스트 실패 |

#### 보안/안정성 (25점 만점)

| 점수 | 기준 |
|------|------|
| **25** | 보안 취약점 없음, 완벽한 에러 핸들링, 입력 검증 완료 |
| **20** | 보안 양호, 사소한 개선점 존재 |
| **15** | 경미한 보안/안정성 이슈, 수정 권고 |
| **10** | 보안/안정성 우려 다수, 수정 필요 |
| **5** | 심각한 보안 취약점 또는 불안정성 |
| **0** | 보안 취약점 또는 시스템 장애 가능 |

### 10.2 전체 평가 기준

| 총점 범위 | 평가 | 의미 | 조치 |
|-----------|------|------|------|
| **80-100** | `PRODUCTION_READY` | 운영 배포 가능 | 승인 |
| **60-79** | `NEEDS_WORK` | 수정 후 재리뷰 필요 | 수정 요청 |
| **0-59** | `NOT_READY` | 상당한 작업 필요 | 반려/재작업 |

### 10.3 Finding Severity별 감점 규칙

| Finding Severity | 감점 | 비고 |
|------------------|------|------|
| **CRITICAL** | 자동 `NOT_READY` | 점수와 무관하게 차단 |
| **HIGH** | -10점 (개당) | 2개 이상 시 `NEEDS_WORK` 이하 |
| **MEDIUM** | -3점 (개당) | - |
| **LOW** | -1점 (개당) | - |
| **INFO** | 0점 | 감점 없음 |

### 10.4 상태 아이콘 기준

| 점수 범위 | 아이콘 | 의미 |
|-----------|--------|------|
| **20-25** | ✅ | 양호 |
| **15-19** | ⚠️ | 주의 필요 |
| **0-14** | ❌ | 개선 필요 |

### 10.5 완성도 리포트 필수 항목

리뷰 완료 시 아래 항목을 포함한 완성도 리포트를 생성합니다:

1. **분류 요약**: 5축 분류 결과 + Review Tier
2. **완성도 평가**: 전체 평가(PRODUCTION_READY/NEEDS_WORK/NOT_READY), 총점, 영역별 점수
3. **발견 사항 요약**: Severity별 Count 및 Categories
4. **상세 Findings**: 개별 Finding 상세 내용
5. **운영 가능성 판단**: 결론, 근거, 필수/권장 수정 사항

> **상세 템플릿**: `__Prompt/Report_Template.md` 참조

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-01-24 | 최초 작성 |
| 1.1.0 | 2026-01-26 | 정량적 복잡도 기준(8.4), 자동 분류 기준(9), 완성도 평가 기준(10) 추가 |
