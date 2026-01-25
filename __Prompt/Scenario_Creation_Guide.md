# Scenario Creation Guide (SSOT)

> **목적**: `_Visualization/senario/` 하위에 신규 시나리오를 생성할 때 참고하는 단일 진실 공급원(Single Source of Truth)

---

## 1. 시나리오 구조 개요

```
_Visualization/
├── senario/
│   ├── Scenario_List.yml          # 전체 시나리오 마스터 인덱스
│   ├── {FLOW_ID}/                  # 플로우 폴더 (CR, ...)
│   │   └── {SCENARIO_ID}_{name}/   # 시나리오 폴더
│   │       ├── graph.yml           # [필수] 프로세스 그래프 IR (SSOT)
│   │       ├── diagram.mermaid     # [선택] Mermaid 다이어그램
│   │       ├── checklist.yml       # [선택] 구현 체크리스트
│   │       └── decisions.yml       # [선택] 아키텍처 결정 기록
│   └── _templates/                 # 템플릿 폴더
│       ├── graph.template.yml
│       ├── diagram.template.mermaid
│       ├── checklist.template.yml
│       └── decisions.template.yml
├── _shared/                        # ⭐ 공통 정의 (SSOT)
│   ├── entities.yml               # 엔티티 레지스트리 (그래프 시각화용)
│   └── actors.yml                 # 액터 상세 정보
└── viewer.html                     # 시나리오 뷰어
```

---

## 2. 신규 시나리오 생성 절차

### Step 1: 시나리오 ID 및 폴더 생성

```bash
# 형식: {FLOW_ID}-{NUMBER}_{snake_case_name}
# 예시: CR-06_pr_template_validation

mkdir _Visualization/senario/{FLOW_ID}/{SCENARIO_ID}_{name}
```

**Flow ID 참조:**
| Flow | 이름                  | 설명                         |
| ---- | -------------------- | ---------------------------- |
| CR   | Code Review Pipeline | 코드 리뷰 파이프라인 시나리오 |

### Step 2: 템플릿 복사

```bash
cp _Visualization/_templates/graph.template.yml \
   _Visualization/senario/{FLOW_ID}/{SCENARIO_FOLDER}/graph.yml
```

### Step 3: graph.yml 작성 (필수)

`graph.yml`은 시나리오의 **SSOT**입니다. Mermaid 다이어그램은 이 파일에서 자동 생성됩니다.

**⭐ 엔티티는 `_shared/entities.yml`에서 참조하세요 (schema v2.0)**

```yaml
schema_version: "2.0"
scenario_id: "CR-06"
scenario_name: "PR Template Validation"
scenario_name_ko: "PR 템플릿 검증"
last_updated: "2026-01-24"

# ⭐ 엔티티 - ref로 _shared/entities.yml 참조 (권장)
entities:
  - ref: "developer"       # Developer 참조
  - ref: "pull_request"    # Pull Request 참조
  - ref: "ci_cd"           # CI/CD Pipeline 참조

  # 커스텀 엔티티 (일회성인 경우만 인라인 정의)
  - id: "pr_template"
    label: "PR Template"
    label_ko: "PR 템플릿"
    type: "artifact"
    color: "#64748b"

# 노드 (프로세스 단계)
nodes:
  - id: "N10"
    entity: "developer"    # entities에서 정의한 ID 참조
    label: "Submit PR"
    label_ko: "PR 제출"
    kind: "start"
    order: 10
    description: "Developer submits pull request"
    description_ko: "개발자가 풀 리퀘스트 제출"

# 엣지 (전환)
edges:
  - id: "E10"
    source: "N10"
    target: "N20"
    label: "validate"
    label_ko: "검증"
    kind: "main"
    order: 11

# 경로 정의
paths:
  main:
    name: "Happy Path"
    name_ko: "정상 경로"
    nodes: ["N10", "N20", "N30"]
```

### 사용 가능한 공유 엔티티 (`_shared/entities.yml`)

**Human Actors:**
| ID | 이름 | 타입 | 색상 |
|----|------|------|------|
| `developer` | Developer / 개발자 | actor | blue |
| `reviewer` | Reviewer / 리뷰어 | actor | emerald |
| `senior_reviewer` | Senior Reviewer / 시니어 리뷰어 | actor | violet |
| `tech_lead` | Tech Lead / 테크 리드 | actor | indigo |
| `architect` | Architect / 아키텍트 | actor | purple |
| `domain_expert` | Domain Expert / 도메인 전문가 | actor | teal |

**Teams:**
| ID | 이름 | 타입 | 색상 |
|----|------|------|------|
| `security_team` | Security Team / 보안팀 | team | red |
| `compliance_team` | Compliance Team / 컴플라이언스팀 | team | amber |
| `sre_team` | SRE Team / SRE팀 | team | cyan |

**Artifacts:**
| ID | 이름 | 타입 | 색상 |
|----|------|------|------|
| `pull_request` | Pull Request / 풀 리퀘스트 | artifact | green |
| `code_diff` | Code Diff / 코드 변경사항 | artifact | lime |
| `review_comment` | Review Comment / 리뷰 코멘트 | artifact | lime-400 |
| `finding` | Finding / 발견사항 | artifact | amber-400 |
| `checklist` | Checklist / 체크리스트 | artifact | blue-400 |

**Systems & Processes:**
| ID | 이름 | 타입 | 색상 |
|----|------|------|------|
| `code_repo` | Code Repository / 코드 저장소 | system | gray-800 |
| `ci_cd` | CI/CD Pipeline / CI/CD 파이프라인 | system | sky |
| `static_analyzer` | Static Analyzer / 정적 분석기 | system | orange |
| `test_runner` | Test Runner / 테스트 러너 | system | cyan-400 |
| `security_scanner` | Security Scanner / 보안 스캐너 | system | red-600 |
| `codeowners` | CODEOWNERS | system | slate |
| `classifier` | PR Classifier / PR 분류기 | process | purple |
| `tier_decision` | Tier Decision / Tier 결정 | process | pink |
| `output_generator` | Output Generator / 출력 생성기 | process | teal |
| `escalation_handler` | Escalation Handler / 에스컬레이션 핸들러 | process | rose |

> 📋 **전체 목록**: `_shared/entities.yml` 참조

### Step 4: Scenario_List.yml 등록

`senario/Scenario_List.yml`의 해당 flow에 시나리오 추가:

```yaml
- id: "CR-06"
  name: "pr_template_validation"
  title: "PR Template Validation"
  title_kr: "PR 템플릿 검증"
  description: "Validate PR description and template compliance"
  status: "draft"
  priority: "medium"
  tags: ["validation", "template", "pr"]
  actors: ["dev", "reviewer"]
  files:
    graph: "CR-06_pr_template_validation/graph.yml"
    checklist: "CR-06_pr_template_validation/checklist.yml"
    decisions: "CR-06_pr_template_validation/decisions.yml"
```

---

## 3. 필수 규칙

### 3.0 ⭐ 엔티티 등록 규칙 (CRITICAL)

> **모든 엔티티는 `_shared/entities.yml`에 등록되어야 합니다.**

#### 왜 중요한가?

- **일관성**: 동일한 엔티티가 시나리오마다 다른 이름/색상으로 표시되면 혼란
- **유지보수성**: 한 곳에서 수정하면 모든 시나리오에 반영
- **검증 가능**: viewer.html이 미등록 엔티티 경고 표시

#### ❌ 금지 사항

```yaml
# ❌ 동일한 엔티티를 다른 이름으로 정의하지 마세요!
entities:
  - id: "dev"           # ❌ → developer 사용
  - id: "pr"            # ❌ → pull_request 사용
  - id: "senior"        # ❌ → senior_reviewer 사용
  - id: "sec_team"      # ❌ → security_team 사용
  - id: "cicd"          # ❌ → ci_cd 사용
  - id: "repo"          # ❌ → code_repo 사용
```

#### ✅ 올바른 사용법

```yaml
# ✅ 등록된 엔티티 ref로 참조
entities:
  - ref: "developer"       # ✅ Developer
  - ref: "reviewer"        # ✅ Reviewer
  - ref: "senior_reviewer" # ✅ Senior Reviewer
  - ref: "pull_request"    # ✅ Pull Request
  - ref: "ci_cd"           # ✅ CI/CD Pipeline
  - ref: "security_team"   # ✅ Security Team
```

#### 🆕 신규 엔티티 등록 절차

새로운 엔티티가 필요한 경우:

1. **먼저 `_shared/entities.yml` 확인** - 이미 등록된 유사 엔티티가 있는지 검색
2. **없으면 등록 요청** - `_shared/entities.yml`에 아래 형식으로 추가:

```yaml
# _shared/entities.yml에 추가
- id: "new_entity_id"        # snake_case, 고유해야 함
  label: "Entity Name"       # 영문 표시명
  label_ko: "엔티티 이름"      # 한글 표시명
  type: "system"             # actor | team | system | artifact | process
  color: "#3b82f6"           # 타입별 색상 팔레트 참고
  description: "Description"
  description_ko: "설명"
  mermaid_alias: "NE"        # Mermaid 다이어그램용 2-4자 약어
  tags: ["category", "tag"]
```

3. **graph.yml에서 ref로 참조**:

```yaml
entities:
  - ref: "new_entity_id"
```

#### 검증 스크립트

엔티티 등록 상태를 확인하려면:

```bash
cd _Visualization
python validate_entities.py
```

---

### 3.1 한글화 (Localization)

모든 사용자 노출 필드에는 `_ko` 버전 필수:

```yaml
# 필수 한글 필드
scenario_name_ko: "..."
label_ko: "..."
description_ko: "..."
title_ko: "..."
name_ko: "..."
```

### 3.2 Node Kind 정의

| kind       | 설명      | 모양        |
| ---------- | --------- | ----------- |
| `start`    | 시작점    | 둥근 사각형 |
| `end`      | 종료점    | 둥근 사각형 |
| `action`   | 일반 액션 | 사각형      |
| `decision` | 분기점    | 다이아몬드  |
| `wait`     | 대기 상태 | 비대칭      |
| `error`    | 에러 상태 | 이중 사각형 |

### 3.3 Edge Kind 정의

| kind         | 설명       | 스타일      |
| ------------ | ---------- | ----------- |
| `main`       | 주요 경로  | 굵은 화살표 |
| `alt`        | 대안 경로  | 일반 화살표 |
| `exception`  | 예외 경로  | 점선 화살표 |
| `background` | 백그라운드 | 긴 점선     |

### 3.4 Status 정의

| status        | 설명         |
| ------------- | ------------ |
| `draft`       | 초안, 미검토 |
| `review`      | 검토 중      |
| `approved`    | 승인됨       |
| `implemented` | 구현 완료    |

### 3.5 Priority 정의

| priority   | 설명             |
| ---------- | ---------------- |
| `critical` | MVP 필수, 블로커 |
| `high`     | MVP 중요         |
| `medium`   | Nice to have     |
| `low`      | 후순위           |

---

## 4. 표준 액터 참조

```yaml
# Code Review Pipeline Actors
# ID: "dev"        - Developer (개발자)
# ID: "reviewer"   - Reviewer (리뷰어)
# ID: "senior"     - Senior Reviewer (시니어 리뷰어)
# ID: "security"   - Security Team (보안팀)
# ID: "compliance" - Compliance Team (컴플라이언스팀)
```

**Entity ID 매핑:**
```yaml
developer:       "dev"       # 개발자
reviewer:        "reviewer"  # 리뷰어
senior_reviewer: "senior"    # 시니어 리뷰어
security_team:   "security"  # 보안팀
compliance_team: "compliance" # 컴플라이언스팀
sre_team:        "sre"       # SRE팀
```

---

## 5. 리뷰 Tier 정의

코드 리뷰 파이프라인에서 사용하는 Tier 체계:

```
CLASSIFY → Risk/Size/Domain/Type/Sensitivity
    ↓
TIER 결정:
┌─────────────────────────────────────────────────────────────┐
│ TIER 1 (Full Deep)     : CRITICAL risk OR Regulated        │
│   → Senior 2+ + Security/Compliance Team                   │
│   → 1-2일 소요                                              │
├─────────────────────────────────────────────────────────────┤
│ TIER 2 (Comprehensive) : HIGH risk OR Large size (201+ LOC)│
│   → Senior 1+ + Domain Expert                              │
│   → 4-8시간 소요                                            │
├─────────────────────────────────────────────────────────────┤
│ TIER 3 (Standard)      : MEDIUM risk OR Medium size        │
│   → 1 Peer Reviewer                                        │
│   → 1-4시간 소요                                            │
├─────────────────────────────────────────────────────────────┤
│ TIER 4 (Light)         : LOW risk + Small size             │
│   → Automated + Optional Quick Review                      │
│   → 30분 이내                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Finding Severity 정의

리뷰 발견사항의 심각도 분류:

| Severity | 설명 | 머지 영향 |
|----------|------|-----------|
| `CRITICAL` | 보안 취약점, 데이터 손실, 시스템 장애 | **머지 차단** |
| `HIGH` | 기능 오동작, 심각한 성능 저하 | 머지 차단 권고 |
| `MEDIUM` | 잠재적 문제, 모범 사례 미준수 | 조건부 승인 가능 |
| `LOW` | 사소한 개선, 코드 스타일 | 승인에 영향 없음 |
| `INFO` | 참고, 제안, 칭찬 | 조치 불필요 |

---

## 7. 체크리스트 (checklist.yml) 카테고리

코드 리뷰 관련 권장 카테고리:

- **Security**: 인증, 권한, 암호화, 취약점
- **Logic**: 비즈니스 로직, 알고리즘, 조건문
- **Performance**: 쿼리 최적화, N+1, 리소스 사용
- **Reliability**: 에러 핸들링, 예외 처리, 안정성
- **Maintainability**: 복잡도, 중복 코드, 가독성
- **Testing**: 테스트 커버리지, 테스트 케이스
- **Documentation**: 주석, API 문서, README
- **Style**: 네이밍, 포맷팅, 컨벤션

---

## 8. 결정 기록 (decisions.yml) 작성

각 시나리오에서 중요한 설계 결정을 기록:

```yaml
decisions:
  - id: "DEC-001"
    title: "Review Tier Auto-assignment"
    title_ko: "리뷰 Tier 자동 할당"
    status: "decided"
    date: "2026-01-24"

    context: |
      Should review tier be auto-assigned or manually selected?
    context_ko: |
      리뷰 Tier를 자동 할당할지 수동 선택할지 결정 필요.

    options:
      - id: "A"
        name: "Full Auto"
        name_ko: "완전 자동"
        pros: ["일관성", "빠른 처리"]
        pros_ko: ["일관성", "빠른 처리"]
        cons: ["유연성 부족"]
        cons_ko: ["유연성 부족"]

      - id: "B"
        name: "Auto with Override"
        name_ko: "자동 + 수동 오버라이드"
        pros: ["일관성", "필요시 조정 가능"]
        pros_ko: ["일관성", "필요시 조정 가능"]
        cons: ["복잡도 증가"]
        cons_ko: ["복잡도 증가"]

    decision: "B"

    rationale: "Automation with flexibility for edge cases"
    rationale_ko: "기본 자동화 + 예외 상황 대응을 위한 수동 오버라이드"
```

---

## 9. 뷰어 실행 방법

```bash
cd _Visualization
python -m http.server 8888
# → http://localhost:8888/viewer.html
```

---

## 10. 자주 하는 실수

| 실수 | 해결 |
|------|------|
| `_ko` 필드 누락 | 모든 label/title/description에 _ko 추가 |
| Scenario_List.yml 미등록 | 시나리오 추가 후 반드시 등록 |
| order 번호 충돌 | main path는 10, 20, 30... / exception은 21, 22... |
| **미등록 엔티티 사용** | `_shared/entities.yml`에 먼저 등록 후 ref로 참조 |
| **동일 엔티티 다른 이름** | `dev` ❌ → `developer` ✅ 사용 |
| 파일 경로 오류 | `files.graph`는 폴더 기준 상대경로 |
| 인라인 엔티티 남용 | 2회 이상 사용되면 `_shared/entities.yml`에 등록 |

---

## 11. 예시: 신규 시나리오 생성 프롬프트

AI에게 시나리오 생성을 요청할 때 사용:

```
@_Visualization/_templates 의 템플릿을 참고하여 다음 시나리오를 생성해줘:

- Flow: CR (Code Review Pipeline)
- ID: CR-06
- Name: pr_template_validation
- 제목: PR Template Validation / PR 템플릿 검증
- 설명: PR 설명과 템플릿 준수 여부를 검증하는 시나리오

필요 파일:
1. graph.yml (필수)
2. checklist.yml
3. decisions.yml

생성 후 Scenario_List.yml에도 등록해줘.
```

---

## 12. 현재 시나리오 커버리지

### 구현됨 ✅
- CR-01: PR Classification (PR 분류)
- CR-02: Review Depth Decision (리뷰 깊이 결정)
- CR-03: Review Execution (리뷰 수행)
- CR-04: Review Output Generation (리뷰 결과 출력)
- CR-05: Escalation Process (에스컬레이션)

### 추가 고려 가능 ⚠️
- `CR-06`: PR Template Validation (PR 템플릿 검증)
- `CR-07`: CODEOWNERS Auto-assignment (자동 리뷰어 할당)
- `CR-08`: Security Scan Integration (보안 스캔 통합)
- `CR-09`: Review Metrics Dashboard (리뷰 지표 대시보드)
- `CR-10`: Pre-commit Hook Integration (Pre-commit 훅 통합)

---

*Last Updated: 2026-01-24*
