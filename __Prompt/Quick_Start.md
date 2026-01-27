# Quick Start Guide - 코드 리뷰 파이프라인

> **목적**: 이 폴더를 다른 레포에 복사하여 Claude AI로 코드 리뷰를 수행하는 방법 안내
> **버전**: 1.0.0
> **최종 업데이트**: 2026-01-26

---

## 1. 설치 (Setup)

### 1.1 복사 방법

#### 방법 A: 단순 복사

```bash
# 전체 폴더를 프로젝트에 복사
cp -r code_review/ /path/to/your-project/

# 또는 필수 파일만 복사
mkdir -p /path/to/your-project/code_review/__Prompt
cp code_review/CLAUDE.md /path/to/your-project/code_review/
cp code_review/__Prompt/*.md /path/to/your-project/code_review/__Prompt/
```

#### 방법 B: Git Subtree

```bash
# 레포를 subtree로 추가
git subtree add --prefix=code_review <repository-url> main --squash

# 업데이트 시
git subtree pull --prefix=code_review <repository-url> main --squash
```

#### 방법 C: Git Submodule

```bash
# 서브모듈로 추가
git submodule add <repository-url> code_review

# 클론 시 서브모듈 포함
git clone --recurse-submodules <your-repo-url>
```

### 1.2 필수 파일 구조

```
your-project/
├── code_review/
│   ├── CLAUDE.md                          # 리뷰 가이드 (SSOT)
│   └── __Prompt/
│       ├── Code_Review_Execution.md       # 실행 프롬프트
│       ├── Report_Template.md             # 리포트 템플릿
│       └── Quick_Start.md                 # 이 파일
└── ... (프로젝트 파일들)
```

---

## 2. 기본 사용법

### 2.1 가장 간단한 사용법

Claude에게 다음과 같이 요청합니다:

```
code_review/CLAUDE.md를 참조하여 다음 코드를 리뷰해줘:

[코드 블록 또는 파일 경로]
```

### 2.2 상세 리뷰 요청

더 정확한 분류를 위해 추가 정보를 제공합니다:

```
code_review/CLAUDE.md 가이드에 따라 코드 리뷰를 수행해줘.

## 리뷰 대상
- 파일: src/payment/checkout.py
- 변경 목적: 결제 실패 시 재시도 로직 추가
- 관련 이슈: #456

## 변경 내용
[git diff 또는 코드 블록]

완성도 리포트까지 생성해줘.
```

### 2.3 PR 리뷰 요청

```
code_review/CLAUDE.md를 따라 이 PR을 리뷰해줘.

PR: [PR 링크 또는 PR 정보]
변경 파일: [파일 목록]
변경 라인: 약 150줄

분류, 리뷰, 완성도 리포트를 생성해줘.
```

---

## 3. 리뷰 프로세스

Claude가 수행하는 4단계 리뷰 프로세스:

```
┌────────────────────────────────────────────────────────────────────┐
│  [1. CLASSIFY] → [2. DEPTH] → [3. REVIEW] → [4. OUTPUT]           │
│                                                                    │
│  1. 분류: Risk, Size, Domain, Type, Sensitivity 판단              │
│  2. 깊이: Tier 1~4 결정                                           │
│  3. 리뷰: Tier별 체크리스트 적용                                   │
│  4. 출력: 완성도 리포트 생성                                       │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 분류 결과 예시

```markdown
### 분류 결과

| 항목 | 값 | 판단 근거 |
|------|-----|-----------|
| Risk Level | HIGH | 결제 관련 코드 |
| Size | M (156줄) | 변경 라인 수 |
| Domain | Core | 핵심 비즈니스 로직 |
| Change Type | Perfective | 기능 개선 |
| Sensitivity | PCI-DSS | 결제 처리 관련 |
| **Review Tier** | TIER 1 | PCI-DSS 민감도 |
```

### 3.2 완성도 평가 예시

```markdown
### 전체 평가: NEEDS_WORK
### 완성도 점수: 72/100

| 영역 | 점수 | 상태 |
|------|------|------|
| 기능 완성도 | 20/25 | ⚠️ |
| 코드 품질 | 20/25 | ⚠️ |
| 테스트 커버리지 | 15/25 | ⚠️ |
| 보안/안정성 | 17/25 | ⚠️ |
```

---

## 4. 고급 사용법

### 4.1 분류 오버라이드

자동 분류가 부정확한 경우 수동으로 조정:

```
코드 리뷰 요청:

파일: src/utils/helper.py

## 분류 오버라이드
- Risk Level: MEDIUM → HIGH (이유: 인증 토큰 관련 유틸리티)
- Domain: Generic → Supporting (이유: 인증 모듈 지원)

위 오버라이드를 적용하여 리뷰해줘.
```

### 4.2 특정 Tier 요청

```
TIER 2 수준으로 다음 코드를 리뷰해줘:

[코드]
```

### 4.3 특정 체크리스트만 적용

```
다음 코드에 대해 보안 체크리스트만 적용하여 리뷰해줘:

[코드]
```

### 4.4 특정 카테고리 집중 리뷰

```
다음 코드를 리뷰해줘. 특히 Performance와 Reliability에 집중해줘:

[코드]
```

---

## 5. 커스터마이징

### 5.1 조직별 커스터마이징 포인트

`CLAUDE.md`에서 다음 항목을 조직에 맞게 수정:

| 섹션 | 항목 | 커스터마이징 내용 |
|------|------|-------------------|
| 2.1 | Risk Level 경로 패턴 | 조직의 디렉토리 구조에 맞게 |
| 2.3 | Domain 판단 기준 | 조직의 도메인 구조에 맞게 |
| 2.5 | Sensitivity 규제 항목 | 적용되는 규제에 맞게 |
| 7.3 | 에스컬레이션 연락처 | 조직의 연락처로 |

### 5.2 커스터마이징 예시

```markdown
## 조직별 Risk Level 경로 패턴 추가

### 2.1 Risk Level 판단 (수정)

| Risk | 경로 패턴 (기존) | 경로 패턴 (추가) |
|------|-----------------|-----------------|
| CRITICAL | `auth/`, `security/` | `billing/`, `kyc/`, `compliance/` |
| HIGH | `core/`, `domain/` | `trade/`, `settlement/` |
```

### 5.3 체크리스트 확장

필요시 Tier별 체크리스트에 항목 추가:

```markdown
#### TIER 1 추가 체크리스트 (우리 조직 전용)

```markdown
## 컴플라이언스 추가 검토
- [ ] KYC 요구사항 충족
- [ ] 자금세탁방지(AML) 규정 준수
- [ ] 금융감독원 가이드라인 확인
```
```

---

## 6. FAQ

### Q1: 어떤 언어를 지원하나요?

**A**: 언어에 구애받지 않습니다. Python, JavaScript, TypeScript, Java, Go, Rust, C++ 등 모든 언어에 적용 가능합니다. 분류 기준은 언어가 아닌 변경의 성격에 기반합니다.

### Q2: 테스트 코드도 리뷰 대상인가요?

**A**: 예. 테스트 코드는 일반적으로 `LOW` Risk로 분류되지만, 테스트 품질은 "테스트 커버리지" 점수에 반영됩니다.

### Q3: 여러 파일을 한번에 리뷰할 수 있나요?

**A**: 예. 관련된 파일들을 함께 제공하면 됩니다:

```
다음 PR의 모든 파일을 리뷰해줘:

파일 1: src/service/user.py
[코드]

파일 2: src/controller/user_controller.py
[코드]

파일 3: tests/test_user.py
[코드]
```

### Q4: 분류가 잘못된 것 같으면 어떻게 하나요?

**A**: 분류 오버라이드를 사용합니다:

```
분류가 잘못된 것 같아. 다음과 같이 오버라이드해줘:
- Risk Level: MEDIUM → HIGH
- 이유: [근거]

오버라이드 적용 후 다시 리뷰해줘.
```

### Q5: 완성도 점수의 의미는?

**A**:
- **80-100점 (PRODUCTION_READY)**: 운영 배포 가능
- **60-79점 (NEEDS_WORK)**: 수정 후 재리뷰 필요
- **0-59점 (NOT_READY)**: 상당한 작업 필요

CRITICAL Finding이 있으면 자동으로 NOT_READY가 됩니다.

### Q6: 리뷰 결과를 어떻게 추적하나요?

**A**: 완성도 리포트를 PR 코멘트로 남기거나, 별도 문서로 저장합니다. 리포트에는 모든 Finding과 권고사항이 포함됩니다.

---

## 7. 프롬프트 템플릿

### 7.1 기본 리뷰 요청

```
code_review/CLAUDE.md를 참조하여 다음 코드를 리뷰해줘:

## 리뷰 대상
- 파일: [파일 경로]
- 변경 목적: [목적]

## 코드
[코드 블록]
```

### 7.2 상세 리뷰 요청

```
code_review/CLAUDE.md 가이드에 따라 코드 리뷰를 수행해줘.

## 리뷰 대상
- 파일: [파일 경로]
- 변경 목적: [목적]
- 관련 이슈: [이슈 번호]
- 변경 규모: 약 [N]줄

## 추가 컨텍스트
[관련 정보]

## 코드
[코드 블록]

다음을 포함해줘:
1. 분류 결과 (5축)
2. Tier 결정
3. 체크리스트 기반 리뷰
4. 완성도 리포트
```

### 7.3 빠른 리뷰 요청

```
다음 코드 간단히 리뷰해줘 (code_review/CLAUDE.md 참조):

[코드 블록]
```

### 7.4 특정 관점 리뷰

```
code_review/CLAUDE.md 가이드 중 보안 체크리스트만 적용하여 다음 코드를 리뷰해줘:

[코드 블록]
```

---

## 8. 문제 해결

### 문제: 분류가 너무 낮게 나옴

**원인**: 경로나 키워드가 인식되지 않음

**해결**:
1. 오버라이드 사용
2. CLAUDE.md의 경로 패턴 커스터마이징

### 문제: 리뷰가 너무 간략함

**원인**: TIER 4로 분류됨

**해결**:
1. 더 높은 Tier 요청
2. 상세 리뷰 요청 프롬프트 사용

### 문제: 특정 규제가 인식 안됨

**원인**: CLAUDE.md에 해당 규제가 없음

**해결**:
1. Sensitivity 오버라이드 사용
2. CLAUDE.md에 규제 추가

---

## 9. 체크리스트: 도입 준비

- [ ] code_review 폴더를 프로젝트에 복사
- [ ] CLAUDE.md의 에스컬레이션 연락처 수정
- [ ] 필요시 Risk Level 경로 패턴 커스터마이징
- [ ] 필요시 Sensitivity 규제 항목 커스터마이징
- [ ] 팀에 사용법 공유
- [ ] 첫 번째 리뷰 테스트

---

## 10. 지원 및 피드백

이슈나 개선 제안이 있으면:
- GitHub Issues에 등록
- 또는 조직 내부 채널 활용

---

*Last Updated: 2026-01-26*
