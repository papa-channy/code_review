# 코드 리뷰 실행 가이드 (Code Review Execution Guide)

> **목적**: Claude AI가 코드 리뷰를 체계적으로 수행하기 위한 실행 프롬프트
> **버전**: 1.0.0
> **최종 업데이트**: 2026-01-26

---

## 개요

이 가이드는 코드 리뷰의 **실행 단계**를 정의합니다. 전체 리뷰 프로세스는 다음과 같이 진행됩니다:

```
┌────────────────────────────────────────────────────────────────────┐
│  [1. 입력 수집] → [2. 자동 분류] → [3. 리뷰 수행] → [4. 리포트]   │
│    정보 확인       5축 분류         체크리스트       완성도 평가    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 1. 입력 정보 수집

### 1.1 필수 정보

| 항목 | 설명 | 수집 방법 |
|------|------|-----------|
| **리뷰 대상** | 파일 경로 또는 코드 블록 | 사용자 제공 또는 git diff |
| **변경 목적** | 변경 이유 (버그 수정, 기능 추가 등) | 커밋 메시지, PR 설명, 사용자 입력 |
| **변경 범위** | 추가/수정/삭제된 코드 라인 수 | git diff 분석 |

### 1.2 선택 정보 (있으면 분류 정확도 향상)

| 항목 | 설명 |
|------|------|
| 관련 이슈/티켓 | 요구사항 추적용 |
| 이전 리뷰 이력 | 반복 이슈 식별 |
| 테스트 결과 | 테스트 커버리지 확인 |
| CI/CD 결과 | 빌드/린트 통과 여부 |

### 1.3 정보 수집 프롬프트 예시

```markdown
코드 리뷰를 시작하겠습니다. 다음 정보를 확인합니다:

1. **리뷰 대상**: [파일 경로 또는 "제공된 코드 블록"]
2. **변경 목적**: [커밋 메시지/PR 설명에서 추출 또는 추론]
3. **변경 규모**: [N줄 추가, M줄 삭제, 총 K줄 변경]
4. **관련 정보**: [이슈 번호, 테스트 결과 등 - 있는 경우]
```

---

## 2. 자동 분류 수행

### 2.1 Risk Level 판단

#### 판단 기준 테이블

| Risk | 경로 패턴 | 키워드 | 변경 내용 |
|------|-----------|--------|-----------|
| **CRITICAL** | `auth/`, `security/`, `payment/`, `crypto/`, `pii/` | password, token, secret, encrypt, decrypt, apikey, credential | 인증/인가 로직, 결제 처리, 암호화, 개인정보 처리 |
| **HIGH** | `core/`, `domain/`, `api/`, `db/`, `schema/` | transaction, migration, contract, interface | 핵심 비즈니스 로직, DB 스키마, API 계약, 트랜잭션 |
| **MEDIUM** | `feature/`, `service/`, `handler/`, `controller/` | - | 일반 기능, 단일 모듈 수정 |
| **LOW** | `docs/`, `test/`, `config/`, `readme`, `.md` | - | 문서, 설정, 테스트 전용 변경 |

#### 판단 알고리즘

```
Risk_Level = CRITICAL  if (경로가 CRITICAL 패턴 포함) OR (CRITICAL 키워드 존재)
           = HIGH      if (경로가 HIGH 패턴 포함) OR (HIGH 키워드 존재)
           = MEDIUM    if (경로가 MEDIUM 패턴 포함) OR (기본값)
           = LOW       if (경로가 LOW 패턴만 포함)
```

### 2.2 Size 계산

#### LOC 기준

| Size | 변경 라인 수 (추가+수정+삭제) | 설명 |
|------|------------------------------|------|
| **XS** | 1~50줄 | 신속 리뷰 가능 |
| **S** | 51~100줄 | 표준 단위 변경 |
| **M** | 101~200줄 | 상세 검토 필요 |
| **L** | 201~500줄 | 분할 권고 |
| **XL** | 500줄+ | **분할 필수** |

#### 계산 방법

```bash
# Git diff 기반 계산
git diff --stat | tail -1  # "N files changed, A insertions(+), D deletions(-)"

# 변경 라인 = insertions + deletions
```

### 2.3 Domain 판단

#### 판단 질문 (순서대로 적용)

```
Q1. 이 코드가 없으면 비즈니스 자체가 성립 불가능한가?
    → YES: Core Domain

Q2. 이 코드가 핵심 기능을 직접 지원하는가? (직접 호출/참조)
    → YES: Supporting Domain

Q3. 이 코드가 범용적이며 외부 라이브러리로 대체 가능한가?
    → YES: Generic Domain
```

#### 경로 기반 힌트

| Domain | 경로 패턴 예시 |
|--------|---------------|
| **Core** | `domain/`, `core/`, `business/`, `order/`, `product/` (도메인 특화) |
| **Supporting** | `service/`, `adapter/`, `integration/`, `notification/` |
| **Generic** | `util/`, `common/`, `lib/`, `helper/`, `infrastructure/` |

### 2.4 Change Type 판단

#### 키워드 기반 분류

| Type | 커밋 메시지/PR 제목 키워드 |
|------|---------------------------|
| **Corrective** | fix, bug, hotfix, patch, resolve, issue, error, defect |
| **Adaptive** | upgrade, migrate, update dependency, version, compatibility |
| **Perfective** | feat, feature, add, implement, enhance, improve, optimize |
| **Preventive** | refactor, restructure, cleanup, tech debt, reorganize |

#### 판단 우선순위

```
1. "fix", "bug" 포함 → Corrective
2. "upgrade", "migrate", "dependency" 포함 → Adaptive
3. "refactor", "cleanup" 포함 → Preventive
4. 기본값 → Perfective (기능 추가/개선)
```

### 2.5 Sensitivity 판단

#### 규제 키워드 및 경로

| Sensitivity | 키워드 | 경로 패턴 | 데이터 타입 |
|-------------|--------|-----------|-------------|
| **SOX** | audit, financial, accounting, journal | `finance/`, `audit/`, `accounting/` | 재무 데이터, 감사 로그 |
| **PCI-DSS** | card, payment, pan, cvv, checkout | `payment/`, `checkout/`, `billing/` | 카드 정보, 결제 데이터 |
| **HIPAA** | patient, medical, health, phi, diagnosis | `health/`, `medical/`, `patient/` | 의료 정보 |
| **GDPR** | personal, pii, consent, user_data, privacy | `user/`, `privacy/`, `consent/` | 개인정보, 동의 데이터 |
| **NONE** | (해당 없음) | (해당 없음) | (해당 없음) |

#### 판단 알고리즘

```
Sensitivity = SOX      if (SOX 키워드 OR 경로 매칭)
            = PCI-DSS  if (PCI-DSS 키워드 OR 경로 매칭)
            = HIPAA    if (HIPAA 키워드 OR 경로 매칭)
            = GDPR     if (GDPR 키워드 OR 경로 매칭)
            = NONE     otherwise
```

### 2.6 분류 결과 출력 형식

```markdown
### 분류 결과

| 항목 | 값 | 판단 근거 |
|------|-----|-----------|
| Risk Level | [CRITICAL/HIGH/MEDIUM/LOW] | [근거] |
| Size | [XS/S/M/L/XL] (N줄) | [라인 수 계산] |
| Domain | [Core/Supporting/Generic] | [판단 질문 결과] |
| Change Type | [Corrective/Adaptive/Perfective/Preventive] | [키워드 근거] |
| Sensitivity | [SOX/PCI-DSS/HIPAA/GDPR/NONE] | [근거] |
```

---

## 3. Tier 결정

### 3.1 Decision Tree 적용

```
START
  │
  ▼
Risk == CRITICAL?  ──YES──►  TIER 1
  │ NO
  ▼
Sensitivity != NONE?  ──YES──►  TIER 1
  │ NO
  ▼
Risk == HIGH?  ──YES──►  TIER 2
  │ NO
  ▼
Size >= L (201줄+)?  ──YES──►  TIER 2
  │ NO
  ▼
Risk == MEDIUM?  ──YES──►  TIER 3
  │ NO
  ▼
Size == M (101~200줄)?  ──YES──►  TIER 3
  │ NO
  ▼
TIER 4
```

### 3.2 Tier별 리뷰 범위

| Tier | 깊이 | 리뷰 범위 |
|------|------|-----------|
| **TIER 1** | Full Deep | 모든 체크리스트 + 아키텍처 분석 + 보안 심층 검토 |
| **TIER 2** | Comprehensive | 공통 + Tier2 체크리스트 + 비즈니스 로직 검증 |
| **TIER 3** | Standard | 공통 + Tier3 체크리스트 + 기능 동작 확인 |
| **TIER 4** | Light | 공통 체크리스트 + 기본 검증 |

---

## 4. 리뷰 수행

### 4.1 공통 체크리스트 (모든 Tier)

```markdown
## 공통 검증 항목
- [ ] 빌드 성공 여부 (CI 결과 확인)
- [ ] 기존 테스트 통과
- [ ] 명백한 보안 취약점 없음
  - [ ] 하드코딩된 시크릿/API 키
  - [ ] SQL 인젝션 가능성
  - [ ] XSS 취약점
- [ ] 코딩 스타일/컨벤션 준수
- [ ] 린트/정적 분석 통과
```

### 4.2 Tier별 체크리스트

#### TIER 1 추가 항목

```markdown
## 보안/컴플라이언스 검토
- [ ] 인증/인가 로직 정확성
- [ ] 암호화 적용 (at-rest, in-transit)
- [ ] 민감 데이터 노출 위험
- [ ] 규제 요구사항 충족 (SOX/PCI/HIPAA/GDPR)
- [ ] 감사 로그 적절성
- [ ] 입력 검증 완전성

## 아키텍처 검토
- [ ] 시스템 설계 원칙 준수
- [ ] 확장성/성능 영향
- [ ] 서비스 간 의존성 변화
- [ ] API 계약 변경 및 하위 호환성
- [ ] 데이터 모델 일관성

## 운영 검토
- [ ] 롤백 계획 수립
- [ ] 배포 전략 적절성
- [ ] 모니터링/알림 설정
- [ ] 장애 시나리오 대응
- [ ] 문서화 완전성
```

#### TIER 2 추가 항목

```markdown
## 비즈니스 로직 검토
- [ ] 요구사항/스토리 충족
- [ ] 엣지 케이스 처리
- [ ] 에러 핸들링 적절성
- [ ] 트랜잭션 일관성
- [ ] 상태 관리 정확성

## 테스트 검토
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 커버리지
- [ ] 테스트 케이스 충분성
- [ ] 회귀 테스트 통과
- [ ] 경계값 테스트

## 성능 검토
- [ ] 쿼리 최적화
- [ ] N+1 문제 없음
- [ ] 메모리/리소스 사용 적절성
- [ ] 캐싱 전략 적절성
```

#### TIER 3 추가 항목

```markdown
## 기능 검토
- [ ] 기능 동작 정상
- [ ] UI/UX 일관성 (해당 시)
- [ ] 로깅 적절성
- [ ] 에러 메시지 명확성

## 코드 품질
- [ ] 코드 가독성
- [ ] 중복 코드 최소화
- [ ] 적절한 네이밍
- [ ] 주석 필요성/적절성
- [ ] 함수/메서드 크기 적절성
```

#### TIER 4 항목

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
- [ ] 근본 원인(Root Cause) 분석 완료
- [ ] 재현 테스트 케이스 포함
- [ ] 회귀 방지 테스트 추가
- [ ] 유사 버그 다른 위치 점검
- [ ] 부작용(Side Effect) 없음 확인
```

#### Adaptive (환경 대응)

```markdown
## 환경 적응 검증
- [ ] 호환성 매트릭스 확인
- [ ] 마이그레이션 스크립트/절차
- [ ] 롤백 절차 수립
- [ ] 의존성 버전 명시
- [ ] 하위 호환성 확인
```

#### Perfective (기능 개선)

```markdown
## 기능 개선 검증
- [ ] 요구사항 추적 (티켓/스토리 연결)
- [ ] 수락 기준 충족
- [ ] 사용자 문서/가이드 업데이트
- [ ] 기능 플래그 적용 (필요 시)
- [ ] 성능 영향 측정
```

#### Preventive (리팩토링)

```markdown
## 리팩토링 검증
- [ ] 기존 동작 유지 (behavior preservation)
- [ ] 복잡도 메트릭 개선 확인
- [ ] 테스트 커버리지 유지/증가
- [ ] 성능 저하 없음
- [ ] 명확한 리팩토링 목적
```

---

## 5. Finding 작성

### 5.1 Finding 구조

각 발견 사항은 다음 형식으로 작성합니다:

```markdown
### Finding #N
**Severity:** [CRITICAL / HIGH / MEDIUM / LOW / INFO]
**Category:** [Security / Logic / Performance / Reliability / Maintainability / Testing / Documentation / Style]
**Location:** `path/to/file.ext:line_number`

**Issue:**
[문제점에 대한 명확한 설명]

**Recommendation:**
[구체적인 해결 방안 또는 개선 제안]

**Code Example:** (선택)
```[language]
// Before
[문제 코드]

// After (권장)
[개선 코드]
```
```

### 5.2 Severity 기준

| Severity | 기준 | 조치 요구 |
|----------|------|-----------|
| **CRITICAL** | 보안 취약점, 데이터 손실, 시스템 장애 가능 | 머지 전 **반드시** 해결 |
| **HIGH** | 기능 오동작, 성능 심각 저하, 요구사항 미충족 | 머지 전 수정 **강력 권고** |
| **MEDIUM** | 잠재적 문제, 모범 사례 미준수, 경미한 버그 | 이번 또는 다음 PR에서 해결 |
| **LOW** | 사소한 개선, 코드 스타일, 가독성 | 선택적 적용 |
| **INFO** | 참고 사항, 제안, 칭찬, 학습 포인트 | 조치 불필요 |

### 5.3 Category 분류

| Category | 검토 포인트 |
|----------|-------------|
| **Security** | 인증/인가, 암호화, 입력 검증, OWASP Top 10 |
| **Logic** | 비즈니스 규칙, 조건문, 알고리즘 정확성 |
| **Performance** | 쿼리 최적화, 리소스 사용, 응답 시간 |
| **Reliability** | 에러 핸들링, 예외 처리, 리소스 관리 |
| **Maintainability** | 복잡도, 중복, 가독성, 모듈화 |
| **Testing** | 테스트 커버리지, 테스트 품질 |
| **Documentation** | 주석, API 문서, README |
| **Style** | 네이밍, 포맷팅, 컨벤션 |

---

## 6. 완성도 평가

### 6.1 영역별 점수 산정

#### 기능 완성도 (25점)

| 점수 | 기준 |
|------|------|
| 25 | 모든 요구사항 완벽 충족, 엣지 케이스 처리 완료 |
| 20 | 핵심 요구사항 충족, 일부 엣지 케이스 미처리 |
| 15 | 주요 기능 동작, 일부 시나리오 미완성 |
| 10 | 기본 기능만 동작, 상당 부분 미완성 |
| 5 | 기능 불완전, 주요 시나리오 실패 |
| 0 | 기능 미동작 |

#### 코드 품질 (25점)

| 점수 | 기준 |
|------|------|
| 25 | 클린 코드, 적절한 추상화, 높은 가독성 |
| 20 | 전반적으로 양호, 사소한 개선점 존재 |
| 15 | 평균 수준, MEDIUM 이하 품질 이슈 존재 |
| 10 | 가독성/유지보수성 문제 다수 |
| 5 | 심각한 코드 스멜, 복잡도 과다 |
| 0 | 이해 불가능한 코드 |

#### 테스트 커버리지 (25점)

| 점수 | 기준 |
|------|------|
| 25 | 커버리지 80%+, 핵심 경로 및 엣지 케이스 테스트 완료 |
| 20 | 커버리지 60-79%, 주요 경로 테스트 완료 |
| 15 | 커버리지 40-59%, 기본 테스트 존재 |
| 10 | 커버리지 20-39%, 테스트 부족 |
| 5 | 커버리지 20% 미만, 최소 테스트만 존재 |
| 0 | 테스트 없음 또는 테스트 실패 |

#### 보안/안정성 (25점)

| 점수 | 기준 |
|------|------|
| 25 | 보안 취약점 없음, 완벽한 에러 핸들링 |
| 20 | 보안 양호, 사소한 개선점 존재 |
| 15 | 경미한 보안/안정성 이슈, 수정 권고 |
| 10 | 보안/안정성 우려 다수, 수정 필요 |
| 5 | 심각한 보안 취약점 또는 불안정성 |
| 0 | 보안 취약점 또는 시스템 장애 가능 |

### 6.2 전체 평가 기준

| 총점 | 평가 | 설명 |
|------|------|------|
| **80-100** | PRODUCTION_READY | 운영 배포 가능 |
| **60-79** | NEEDS_WORK | 수정 후 재리뷰 필요 |
| **0-59** | NOT_READY | 상당한 작업 필요, 배포 불가 |

### 6.3 Severity별 감점

| Finding Severity | 감점 |
|------------------|------|
| CRITICAL | 평가 자동 **NOT_READY** |
| HIGH | -10점 (개당) |
| MEDIUM | -3점 (개당) |
| LOW | -1점 (개당) |
| INFO | 0점 |

---

## 7. 리포트 생성

리뷰 완료 후 `Report_Template.md`의 형식에 따라 완성도 리포트를 생성합니다.

### 7.1 리포트 포함 항목

1. **분류 요약**: 5축 분류 결과 및 Review Tier
2. **완성도 평가**: 총점, 영역별 점수, 상태 아이콘
3. **발견 사항 요약**: Severity별 개수 및 카테고리
4. **상세 Findings**: 개별 Finding 상세 내용
5. **운영 가능성 판단**: 결론, 근거, 필수/권장 수정 사항

### 7.2 리포트 출력 예시

```markdown
# 코드 리뷰 완성도 리포트

## 1. 분류 요약
| 항목 | 값 |
|------|-----|
| Risk Level | HIGH |
| Size | M (156줄) |
| Domain | Supporting |
| Change Type | Perfective |
| Sensitivity | NONE |
| **Review Tier** | TIER 2 |

## 2. 완성도 평가
### 전체 평가: NEEDS_WORK
### 완성도 점수: 72/100

| 영역 | 점수 | 상태 |
|------|------|------|
| 기능 완성도 | 20/25 | ⚠️ |
| 코드 품질 | 20/25 | ⚠️ |
| 테스트 커버리지 | 15/25 | ⚠️ |
| 보안/안정성 | 17/25 | ⚠️ |

## 3. 발견 사항 요약
| Severity | Count | Categories |
|----------|-------|------------|
| Critical | 0 | - |
| High | 1 | Logic |
| Medium | 3 | Testing, Maintainability, Documentation |
| Low | 2 | Style |

...
```

---

## 8. 분류 오버라이드

자동 분류가 부정확한 경우, 사용자가 수동으로 오버라이드할 수 있습니다.

### 8.1 오버라이드 요청 형식

```markdown
## 분류 오버라이드

다음 항목을 수동으로 조정합니다:

| 항목 | 자동 분류 | 오버라이드 | 사유 |
|------|-----------|------------|------|
| Risk Level | MEDIUM | HIGH | [사유 작성] |
| Domain | Generic | Core | [사유 작성] |
```

### 8.2 오버라이드 적용

오버라이드가 적용되면:
1. 해당 분류값을 오버라이드 값으로 대체
2. Tier 재계산
3. 리뷰 체크리스트 재선택
4. 리포트에 "수동 오버라이드 적용됨" 표시

---

## 9. 사용 예시

### 9.1 코드 리뷰 요청 프롬프트

```
다음 코드를 리뷰해주세요:

파일: src/payment/processor.py
변경 목적: 결제 검증 로직 버그 수정
관련 이슈: #1234

[코드 블록 또는 git diff]
```

### 9.2 Claude 응답 흐름

```
1. 입력 정보 확인
2. 자동 분류 수행 → 결과 출력
3. Tier 결정 → TIER 1 (CRITICAL + PCI-DSS)
4. 해당 체크리스트 적용하여 리뷰 수행
5. Findings 작성
6. 완성도 평가
7. 리포트 생성
```

---

*Last Updated: 2026-01-26*
