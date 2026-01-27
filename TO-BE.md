# TO-BE: 코드 리뷰 파이프라인 개선 방향

> **목적**: 프로덕션 수준의 코드 리뷰 시스템으로 발전하기 위한 개선 로드맵
> **기준일**: 2026-01-27
> **현재 성숙도**: Level 1.2 (AS-IS.md 참조)
> **목표 성숙도**: Level 3.0+ (Measured)

---

## 1. 목표 상태 (Target State)

### 1.1 목표 파이프라인 전체 사이클

```
현재 커버리지 (~35%):
                    ┌──────────────────────────┐
[코딩] → [Pre-commit] → [PR 제출] → [자동 분석] → [사람 리뷰] → [승인] → [머지] → [배포] → [모니터링] → [인시던트] → [포스트모텀] → [개선]

목표 커버리지 (~90%):
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
[코딩] → [Pre-commit] → [PR 제출] → [자동 분석] → [사람 리뷰] → [승인 강제] → [머지] → [배포] → [모니터링] → [인시던트] → [포스트모텀] → [개선]
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 목표 프로세스 성숙도

| 영역 | AS-IS | TO-BE | 변화 |
|------|-------|-------|------|
| 분류 체계 | Level 2 | Level 3 | CI 연동 자동 분류 + 메트릭 |
| 리뷰 깊이 | Level 1 | Level 2 | 자동 Tier 할당 + CODEOWNERS |
| 체크리스트 | Level 1 | Level 2 | 자동화 게이트 + 수동 체크 이원화 |
| 출력 형식 | Level 2 | Level 3 | 메트릭 연동 리포트 |
| 승인 모델 | Level 0 | Level 2 | 3단 승인 + Branch Protection |
| 자동화 | Level 0 | Level 2 | CI/CD 통합, SAST/SCA |
| Post-Merge | Level 0 | Level 2 | 카나리 배포, 모니터링, 포스트모텀 |
| 메트릭 | Level 0 | Level 3 | DORA 메트릭 + 리뷰 메트릭 |
| DX | Level 1 | Level 2 | 도구 통합, 원클릭 설정 |

### 1.3 목표 상태의 핵심 원칙

```
1. 기계가 잡을 수 있는 것은 기계가 잡는다
   → 사람은 비즈니스 로직, 아키텍처, 설계 판단에 집중

2. 올바른 선택이 쉬운 선택이다 (Paved Roads)
   → 복사해서 붙이면 바로 작동하는 설정 파일 제공

3. 측정하지 않으면 개선할 수 없다
   → 리뷰 메트릭 수집 → 분석 → 프로세스 개선 루프

4. 머지는 끝이 아니라 시작이다
   → Post-Merge 모니터링 + 인시던트 대응 + 포스트모텀
```

---

## 2. 개선 로드맵

### 2.1 Phase 개요

```
Phase 1: 기반 강화         ← 문서 레벨 (현재 자산 확장)
Phase 2: 자동화 연동       ← 도구 레벨 (CI/CD, SAST, Hook)
Phase 3: 프로세스 확장     ← 조직 레벨 (Post-Merge, Postmortem)
Phase 4: 지속적 개선       ← 문화 레벨 (메트릭, 피드백 루프)
```

### 2.2 Phase별 상세

---

## Phase 1: 기반 강화 — 문서 레벨

> **목표**: 현재 문서 기반 자산을 프로덕션 팀 수준으로 보강
> **성격**: 문서 추가/수정, 코드 변경 없음

### P1-1. 승인 모델 정의

**현재**: Tier별 "시니어 N인 필요" 권고만 존재
**목표**: Google 3-bit 모델 기반의 명시적 승인 구조

```
목표 승인 모델:

┌─────────────────────────────────────────────────────────────────┐
│  Approval Bit 1: LGTM (코드 로직 승인)                         │
│  → 작성자 외 최소 1인이 코드 로직을 확인                        │
│                                                                 │
│  Approval Bit 2: OWNERSHIP (코드 소유권 승인)                   │
│  → 변경된 경로의 CODEOWNERS에 등록된 팀/개인이 승인             │
│                                                                 │
│  Approval Bit 3: EXPERTISE (전문성 승인)                        │
│  → Tier 1: 보안/컴플라이언스 전문가                             │
│  → Tier 2: 도메인 전문가                                        │
│  → Tier 3-4: LGTM으로 충분                                     │
└─────────────────────────────────────────────────────────────────┘
```

**산출물**: `CLAUDE.md`에 승인 모델 섹션 추가

### P1-2. CODEOWNERS 가이드 및 템플릿

**현재**: "CODEOWNERS: 경로 기반 리뷰어 자동 할당" 한 줄 언급
**목표**: 복사해서 바로 쓸 수 있는 CODEOWNERS 템플릿 + 작성 가이드

```
# 예시 CODEOWNERS

# 기본 리뷰어 (fallback)
* @org/core-team

# 보안 관련 (CRITICAL)
/src/auth/          @org/security-team @org/senior-devs
/src/security/      @org/security-team
/src/payment/       @org/security-team @org/payment-team

# 핵심 도메인 (Core)
/src/domain/        @org/domain-experts @org/senior-devs
/src/core/          @org/senior-devs

# 인프라/설정
/infrastructure/    @org/sre-team
/.github/           @org/devops-team
```

**산출물**: `__Prompt/CODEOWNERS_Guide.md`

### P1-3. Post-Merge 체크리스트

**현재**: 완전 부재
**목표**: 머지 후 수행해야 할 검증 프로세스 정의

```
## Post-Merge 체크리스트

### 배포 전
- [ ] 카나리 배포 비율 설정 (권장: 0.5% → 1% → 5% → 25% → 100%)
- [ ] 롤백 기준 정의 (에러율, 레이턴시, 비즈니스 메트릭)
- [ ] 모니터링 대시보드 확인

### 배포 중
- [ ] 카나리 메트릭 정상 범위 내
- [ ] 에러 로그 이상 없음
- [ ] 비즈니스 메트릭 변동 없음

### 배포 후 (24시간)
- [ ] 주요 지표 안정화 확인
- [ ] Feature Flag 정리 계획 수립 (해당 시)
- [ ] 관련 문서 업데이트
```

**산출물**: `CLAUDE.md`에 Post-Merge 섹션 추가

### P1-4. Blameless Postmortem 가이드

**현재**: 완전 부재
**목표**: 인시던트 발생 시 구조화된 사후 분석 프로세스

```
## Postmortem 템플릿

### 인시던트 개요
- 발생 시간, 영향 범위, 심각도

### 타임라인
- 발생 → 감지 → 에스컬레이션 → 완화 → 해결 → 종료

### 근본 원인 (5 Whys)
- Why 1 → Why 2 → Why 3 → Why 4 → Why 5

### 교훈 (Lessons Learned)
- 잘한 점 / 개선할 점 / 행운이었던 점

### 후속 조치 (Action Items)
- 담당자, 기한, 추적 방법
```

**산출물**: `__Prompt/Postmortem_Guide.md`

### P1-5. 리뷰 메트릭 정의

**현재**: 미정의
**목표**: 추적할 핵심 메트릭과 목표값 정의

| 메트릭 | 정의 | 목표값 | 벤치마크 |
|--------|------|--------|----------|
| **첫 응답 시간** | PR 생성 → 첫 리뷰 코멘트 | < 4시간 | Google < 1시간 |
| **리뷰 완료 시간** | PR 생성 → 최종 승인 | < 24시간 | Google < 4시간 |
| **PR 크기** | 변경 라인 수 중앙값 | < 200줄 | Google 24줄 |
| **리뷰 라운드** | 승인까지 리뷰 왕복 횟수 | < 3회 | - |
| **머지 후 결함률** | 머지 후 발견된 버그 비율 | < 5% | - |
| **리뷰어 부하** | 리뷰어당 주간 리뷰 건수 | < 10건 | - |

**산출물**: `CLAUDE.md`에 메트릭 섹션 추가

---

## Phase 2: 자동화 연동 — 도구 레벨

> **목표**: CI/CD와 연동하여 기계적 검증을 자동화
> **성격**: 설정 파일, 스크립트, CI 파이프라인 코드

### P2-1. Pre-commit Hook 설정

**현재**: 없음
**목표**: 복사해서 바로 쓸 수 있는 pre-commit 설정

```yaml
# .pre-commit-config.yaml (예시)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key        # 시크릿 감지

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff                       # Python 린트
      - id: ruff-format               # Python 포맷

  # 언어별 확장 포인트
```

**산출물**: `__Prompt/PreCommit_Setup.md` + 언어별 예시 설정

### P2-2. CI/CD 통합 명세

**현재**: "CI/CD: 빌드, 테스트, 린트, 보안 스캔 자동 실행" 한 줄
**목표**: GitHub Actions / GitLab CI에서의 실제 파이프라인 설정

```yaml
# 목표 CI 파이프라인 구조
#
# PR Open/Update 시:
#   ┌─ [Stage 1: Fast Checks]          (< 2분)
#   │   ├─ 린트 (Ruff/ESLint)
#   │   ├─ 포맷 검증
#   │   └─ 시크릿 스캔
#   │
#   ├─ [Stage 2: Build & Test]         (< 10분)
#   │   ├─ 빌드
#   │   ├─ 단위 테스트
#   │   └─ 커버리지 리포트
#   │
#   ├─ [Stage 3: Security]             (< 5분)
#   │   ├─ SAST (Semgrep/SonarQube)
#   │   ├─ SCA (Dependency Check)
#   │   └─ 라이선스 검사
#   │
#   └─ [Stage 4: Auto Classification]  (< 1분)
#       ├─ PR 크기 계산 + 라벨 부착
#       ├─ 경로/키워드 기반 Risk 라벨
#       └─ 대형 PR 경고
```

**산출물**: `__Prompt/CI_Integration_Guide.md` + GitHub Actions 예시

### P2-3. SAST/SCA 도구 연동

**현재**: "보안 취약점 없음" 수동 체크
**목표**: 자동 보안 스캔 + 임계값 기반 머지 차단

```
도구 추천:

SAST (정적 분석):
  - Semgrep (오픈소스, 규칙 커스터마이징 용이)
  - SonarQube (종합 품질 + 보안)

SCA (의존성 분석):
  - Snyk (의존성 취약점)
  - OWASP Dependency-Check (오픈소스)

시크릿 감지:
  - Gitleaks (pre-commit + CI 양쪽)
  - TruffleHog

임계값:
  - CRITICAL: 머지 차단 (자동)
  - HIGH: 머지 차단 (보안팀 오버라이드 가능)
  - MEDIUM: 경고 (머지 허용)
  - LOW: 정보 표시
```

**산출물**: `__Prompt/Security_Scanning_Guide.md`

### P2-4. Branch Protection 설정 가이드

**현재**: "Branch Protection: Tier별 승인 규칙 적용" 한 줄
**목표**: Tier별 Branch Protection 실제 설정 방법

```
Tier별 Branch Protection 매핑:

TIER 1 (Critical/Regulated):
  - Required reviewers: 2+
  - Required CODEOWNERS review: Yes
  - Required status checks: lint, test, sast, sca
  - Dismiss stale reviews: Yes
  - Require linear history: Yes

TIER 2 (High/Large):
  - Required reviewers: 2
  - Required CODEOWNERS review: Yes
  - Required status checks: lint, test, sast

TIER 3 (Standard):
  - Required reviewers: 1
  - Required status checks: lint, test

TIER 4 (Light):
  - Required reviewers: 1 (or auto-merge for trusted bots)
  - Required status checks: lint, test
```

**산출물**: `__Prompt/BranchProtection_Guide.md`

### P2-5. PR 크기 자동 경고

**현재**: "XL은 분할 필수"라고 권고
**목표**: CI에서 PR 크기 자동 계산 + 라벨 + 경고

```
# PR Size Bot 동작:
#
# 1. PR 변경 라인 수 계산 (additions + deletions)
# 2. 크기 라벨 자동 부착:
#    - size/XS (1-50)
#    - size/S  (51-100)
#    - size/M  (101-200)
#    - size/L  (201-500)  → 경고 코멘트
#    - size/XL (500+)     → 분할 요청 코멘트
# 3. Risk 라벨 자동 부착 (경로 패턴 기반)
```

**산출물**: CI 파이프라인 예시 코드에 포함

---

## Phase 3: 프로세스 확장 — 조직 레벨

> **목표**: 머지 후 프로세스와 조직 차원의 실천 방안 정의
> **성격**: 프로세스 가이드, 조직 정책

### P3-1. 카나리 배포 가이드

**현재**: "배포 전략 (Blue-Green, Canary 등)" 체크만
**목표**: 단계별 카나리 배포 프로세스 + 롤백 기준

```
카나리 배포 프로세스:

Stage 1: Canary (0.5~1%)
  └─ 관찰: 15분
  └─ 기준: 에러율 < 0.1%, p99 레이턴시 < 기준의 1.2배
  └─ 실패 시: 자동 롤백

Stage 2: Limited (5%)
  └─ 관찰: 30분
  └─ 기준: Stage 1과 동일 + 비즈니스 메트릭 정상
  └─ 실패 시: 자동 롤백

Stage 3: Expanded (25%)
  └─ 관찰: 1시간
  └─ 기준: 모든 메트릭 안정
  └─ 실패 시: 수동 판단 + 롤백

Stage 4: Full (100%)
  └─ 관찰: 24시간
  └─ 기준: SLO 달성
```

**산출물**: `__Prompt/Canary_Deployment_Guide.md`

### P3-2. 모니터링 체크리스트

**현재**: "모니터링/알림 설정" 체크만
**목표**: 배포 후 확인해야 할 구체적 관측 포인트

```
## 모니터링 관측 포인트

### 인프라 레이어
- CPU/Memory 사용률
- 디스크 I/O
- 네트워크 트래픽

### 애플리케이션 레이어
- 에러율 (4xx, 5xx)
- 응답 시간 (p50, p95, p99)
- 처리량 (RPS)
- 큐 깊이 (해당 시)

### 비즈니스 레이어
- 핵심 전환율 (결제, 가입 등)
- 사용자 이탈률
- 비즈니스 KPI

### 알림 기준
- WARNING: p99 > 기준의 1.5배
- CRITICAL: 에러율 > 1% 또는 p99 > 기준의 3배
- PAGE: 에러율 > 5% 또는 서비스 다운
```

**산출물**: `CLAUDE.md` Post-Merge 섹션에 통합

### P3-3. Feature Flag 운영 가이드

**현재**: "기능 플래그 적용 (필요 시)" 체크만
**목표**: Feature Flag 생성부터 제거까지 전체 라이프사이클

```
Feature Flag 라이프사이클:

1. 생성
   - 명명 규칙: {team}_{feature}_{date} (예: payment_retry_20260127)
   - 기본값: OFF
   - 소유자: 기능 담당 팀

2. 점진적 활성화
   - 내부 테스터 → 직원 → 1% → 5% → 25% → 100%

3. 정리 (최대 수명: 90일)
   - Full rollout 확인 후 플래그 제거 PR 생성
   - 플래그 코드 제거 + 테스트 업데이트

4. 위험 관리
   - 스테일 플래그 알림 (30일/60일/90일)
   - 플래그 의존성 그래프 관리
   - Kill switch: 긴급 시 즉시 OFF
```

**산출물**: `__Prompt/FeatureFlag_Guide.md`

### P3-4. Postmortem 프로세스 확립

**현재**: 완전 부재
**목표**: Meta SEV 모델 기반 인시던트 → 학습 루프

```
인시던트 대응 → 포스트모텀 루프:

[인시던트 발생]
  ↓
[감지] ← 모니터링 알림
  ↓
[에스컬레이션] → 인시던트 오너 지정
  ↓
[완화] → 롤백, 핫픽스, 우회
  ↓
[해결] → 근본 원인 수정
  ↓
[포스트모텀] ← 24~72시간 내 수행
  │
  ├─ What: 무슨 일이 일어났는가 (타임라인)
  ├─ Why: 근본 원인 (5 Whys)
  ├─ Learn: 무엇을 배웠는가
  └─ Action: 재발 방지 조치
  ↓
[프로세스 개선] → 체크리스트/가이드 업데이트
  ↓
[반복]
```

**산출물**: `__Prompt/Postmortem_Guide.md` (P1-4에서 생성, P3에서 프로세스화)

---

## Phase 4: 지속적 개선 — 문화 레벨

> **목표**: 데이터 기반 프로세스 개선 문화 확립
> **성격**: 메트릭 체계, 피드백 루프, 교육 프로그램

### P4-1. 리뷰 메트릭 대시보드

**현재**: 측정 없음
**목표**: 핵심 메트릭 자동 수집 + 시각화

```
## 수집 메트릭

### 속도 메트릭
- Time to First Review (TTFR)
- Time to Approval (TTA)
- PR Cycle Time (생성 → 머지)

### 품질 메트릭
- Post-Merge Defect Rate
- Review Comment Density
- Revert Rate

### 부하 메트릭
- Reviews per Reviewer per Week
- PR Queue Depth
- Reviewer Response Distribution

### DORA 메트릭
- Deployment Frequency
- Lead Time for Changes
- Change Failure Rate
- Mean Time to Recovery (MTTR)
```

**산출물**: 메트릭 정의서 + 대시보드 설정 가이드

### P4-2. 리뷰 품질 피드백 루프

**현재**: 없음
**목표**: 리뷰 유용성 평가 → 프로세스 개선 사이클

```
피드백 루프:

[리뷰 완료]
  ↓
[개발자 평가] ← "이 리뷰가 도움이 되었나요?" (Uber 모델)
  ↓
[데이터 수집] → 유용한/유용하지 않은 코멘트 패턴 분석
  ↓
[분석] → 체크리스트 효과성, Finding 정확도 평가
  ↓
[개선]
  ├─ 체크리스트 항목 추가/제거
  ├─ 분류 기준 조정
  └─ 리뷰어 교육 포인트 도출
  ↓
[반영] → CLAUDE.md 업데이트
  ↓
[반복] (월간 사이클)
```

### P4-3. Readability 프로그램 (선택)

**현재**: 없음
**목표**: Google 모델 기반 언어별 코드 품질 전문가 인증

```
Readability 프로그램:

자격 요건:
  - 해당 언어 리뷰 50건 이상 수행
  - 시니어 Readability 홀더의 승인

역할:
  - TIER 1/2 리뷰 시 최소 1인의 Readability 홀더 참여
  - 스타일 가이드 유지보수
  - 신규 팀원 온보딩 리뷰

혜택:
  - 코드 품질 일관성 유지
  - 지식 전파 채널
  - 리뷰어 전문성 가시화
```

### P4-4. 지식 공유 메커니즘

```
지식 공유 채널:

1. 리뷰를 통한 학습 (기본)
   - 모든 리뷰 코멘트에 "왜"를 포함
   - INFO Finding으로 좋은 패턴 칭찬

2. 주간 리뷰 하이라이트 (권장)
   - 이번 주 흥미로운 Finding 공유
   - 반복되는 패턴 → 가이드/린트 규칙화

3. 포스트모텀 공유 (필수)
   - 인시던트에서 배운 점을 전체 팀에 공유
   - 관련 체크리스트 즉시 업데이트
```

---

## 3. 우선순위 매트릭스

### 3.1 Impact vs Effort

```
                          HIGH IMPACT
                              │
               P1-1           │           P2-2
            승인 모델          │         CI 통합
                              │
               P1-3           │           P2-1
            Post-Merge        │        Pre-commit
                              │
  LOW EFFORT ─────────────────┼───────────────────── HIGH EFFORT
                              │
               P1-2           │           P3-1
            CODEOWNERS        │        카나리 배포
                              │
               P1-5           │           P4-1
            메트릭 정의        │        대시보드
                              │
                          LOW IMPACT
```

### 3.2 권장 실행 순서

| 순서 | ID | 항목 | 이유 |
|------|-----|------|------|
| 1 | P1-1 | 승인 모델 정의 | 가장 큰 Gap, 문서 추가만으로 가능 |
| 2 | P1-3 | Post-Merge 체크리스트 | 커버리지 가장 큰 확장, 문서만 필요 |
| 3 | P1-2 | CODEOWNERS 가이드 | 승인 모델의 실행 기반 |
| 4 | P1-4 | Postmortem 가이드 | Post-Merge의 학습 루프 |
| 5 | P1-5 | 메트릭 정의 | 이후 개선의 기준선 |
| 6 | P2-1 | Pre-commit Hook | 가장 쉬운 자동화 |
| 7 | P2-2 | CI 통합 명세 | 핵심 자동화 |
| 8 | P2-3 | SAST/SCA 연동 | 보안 자동화 |
| 9 | P2-4 | Branch Protection | 승인 강제 |
| 10 | P2-5 | PR 크기 경고 | 품질 자동화 |

---

## 4. 산출물 요약

### 4.1 Phase 1 산출물 (문서)

| 파일 | 유형 | 설명 |
|------|------|------|
| `CLAUDE.md` 승인 모델 섹션 | 수정 | 3단 승인 구조 정의 |
| `CLAUDE.md` Post-Merge 섹션 | 수정 | 배포/모니터링/롤백 체크리스트 |
| `CLAUDE.md` 메트릭 섹션 | 수정 | 핵심 메트릭 + 목표값 |
| `__Prompt/CODEOWNERS_Guide.md` | 신규 | CODEOWNERS 작성 가이드 + 템플릿 |
| `__Prompt/Postmortem_Guide.md` | 신규 | Blameless Postmortem 템플릿 + 프로세스 |

### 4.2 Phase 2 산출물 (자동화)

| 파일 | 유형 | 설명 |
|------|------|------|
| `__Prompt/PreCommit_Setup.md` | 신규 | pre-commit 설정 가이드 + 언어별 예시 |
| `__Prompt/CI_Integration_Guide.md` | 신규 | GitHub Actions/GitLab CI 파이프라인 가이드 |
| `__Prompt/Security_Scanning_Guide.md` | 신규 | SAST/SCA 도구 설정 가이드 |
| `__Prompt/BranchProtection_Guide.md` | 신규 | Tier별 Branch Protection 설정 |

### 4.3 Phase 3 산출물 (프로세스)

| 파일 | 유형 | 설명 |
|------|------|------|
| `__Prompt/Canary_Deployment_Guide.md` | 신규 | 카나리 배포 프로세스 |
| `__Prompt/FeatureFlag_Guide.md` | 신규 | Feature Flag 라이프사이클 |

### 4.4 Phase 4 산출물 (문화)

| 파일 | 유형 | 설명 |
|------|------|------|
| 메트릭 대시보드 가이드 | 신규 | 수집 메트릭 + 시각화 설정 |
| 피드백 루프 설계 | 신규 | 리뷰 품질 → 프로세스 개선 사이클 |

---

## 5. 성공 지표

### 5.1 Phase별 완료 기준

| Phase | 완료 기준 | 목표 성숙도 |
|-------|-----------|-------------|
| **Phase 1** | 모든 문서 작성 완료, 팀 리뷰 통과 | Level 1.5 |
| **Phase 2** | CI에서 자동 린트/테스트/보안 스캔 실행 | Level 2.0 |
| **Phase 3** | 카나리 배포 1회 이상 실행, 포스트모텀 1회 이상 수행 | Level 2.5 |
| **Phase 4** | 메트릭 대시보드 운영, 월간 개선 사이클 1회 이상 | Level 3.0 |

### 5.2 목표 충족 체크리스트

```
업계 기준 충족:
  Phase 1 후:
    ✅ 승인 모델 정의
    ✅ Post-Merge 프로세스 정의
    ✅ 포스트모텀 가이드
    ✅ 메트릭 정의

  Phase 2 후:
    ✅ 자동 빌드/테스트 게이트
    ✅ CODEOWNERS 기반 리뷰어 할당
    ✅ SAST/SCA 보안 스캔
    ✅ Pre-commit Hook
    ✅ PR 크기 자동 경고

  Phase 3 후:
    ✅ 카나리 배포
    ✅ Post-Merge 모니터링
    ✅ Feature Flag 운영
    ✅ 인시던트 포스트모텀

  Phase 4 후:
    ✅ 리뷰 메트릭 추적
    ✅ 피드백 루프 운영
    ✅ 지속적 개선 문화
```

---

## 6. 리스크 및 주의사항

| 리스크 | 영향 | 대응 |
|--------|------|------|
| **과도한 프로세스로 속도 저하** | 개발자 생산성 하락 | 자동화 우선, 수동 체크 최소화. Netflix "Paved Roads" 원칙 적용 |
| **도구 도입 비용** | 라이선스, 학습 곡선 | 오픈소스 우선 (Semgrep, Ruff, pre-commit), 점진적 도입 |
| **조직 저항** | 프로세스 무시 | Phase 1(문서)부터 단계적 도입, 성공 사례 먼저 만들기 |
| **메트릭 과집착** | Goodhart's Law | 메트릭은 방향 확인용. 목표가 아닌 지표로 활용 |
| **컨텍스트 무시** | 모든 팀에 동일 기준 적용 | Tier 시스템 활용, 팀별 커스터마이징 허용 |

---

## 7. 요약

### AS-IS → TO-BE 변화

```
AS-IS (현재):
  "무엇을 검토해야 하는가" ← 잘 정의됨
  "어떻게 강제하는가"      ← 없음
  "머지 후에는 무엇을"     ← 없음
  "어떻게 개선하는가"      ← 없음

TO-BE (목표):
  "무엇을 검토해야 하는가" ← 유지 + 승인 모델 추가
  "어떻게 강제하는가"      ← CI/CD + Branch Protection + CODEOWNERS
  "머지 후에는 무엇을"     ← 카나리 배포 + 모니터링 + 포스트모텀
  "어떻게 개선하는가"      ← 메트릭 + 피드백 루프 + 지식 공유
```

### 한 줄 목표

> **"리뷰 가이드"에서 "리뷰 시스템"으로 — 자동화, 강제, 관측, 학습의 전체 사이클을 갖춘 프로덕션급 코드 리뷰 파이프라인**

---

*Last Updated: 2026-01-27*
