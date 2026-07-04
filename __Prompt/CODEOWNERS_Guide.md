# CODEOWNERS 작성 가이드

> **목적**: 경로 기반 리뷰어 자동 할당으로 승인 모델(`Review_Pipeline_Guide.md` Section 11)의 OWNERSHIP 비트를 실행 가능하게 만듭니다.
> **참조**: Review_Pipeline_Guide.md Section 9.1 (경로 패턴), Section 11 (승인 모델), TO-BE.md P1-2

---

## 1. CODEOWNERS란

- GitHub/GitLab이 PR 생성 시 **변경된 파일 경로에 매칭되는 소유자를 자동으로 리뷰어로 지정**하는 메커니즘입니다.
- 파일 위치: `.github/CODEOWNERS` (GitHub 권장), 루트 또는 `docs/`도 가능
- Branch Protection의 "Require review from Code Owners"와 결합하면 OWNERSHIP 승인을 **강제**할 수 있습니다 (Phase 2, TO-BE.md P2-4).

---

## 2. 문법 핵심 규칙

```
# 패턴          소유자 (복수 가능)
/src/auth/      @org/security-team @org/senior-devs
```

| 규칙 | 내용 |
|------|------|
| **마지막 매칭 우선** | 여러 패턴에 매칭되면 **가장 아래쪽 규칙 하나만** 적용됨. 가장 흔한 실수 원인 |
| **소유자 표기** | 팀 `@org/team-name`, 개인 `@username`, 이메일 가능 |
| **패턴 문법** | `.gitignore`와 유사. `*` 와일드카드, `/` 시작 시 루트 기준 |
| **소유자 없는 패턴** | 패턴만 쓰고 소유자를 비우면 해당 경로는 "소유자 없음"으로 명시적 제외 |
| **팀 권한** | GitHub에서 팀은 해당 저장소에 **write 권한**이 있어야 자동 할당됨 |

---

## 3. 템플릿 (복사해서 사용)

Risk Level 자동 분류(`Review_Pipeline_Guide.md` Section 9.1)의 경로 패턴과 정렬된 템플릿입니다. **마지막 매칭이 우선이므로, 일반 규칙을 위에, 민감한 경로를 아래에** 배치합니다.

```
# ============================================================
# CODEOWNERS — Risk 기반 리뷰어 자동 할당
# 규칙: 마지막 매칭 하나만 적용됨. 민감한 경로일수록 아래쪽에 배치.
# ============================================================

# ---- 기본 (fallback): 모든 파일 ----
*                       @org/core-team

# ---- LOW: 문서/테스트 ----
/docs/                  @org/docs-team
*.md                    @org/docs-team

# ---- MEDIUM: 일반 기능 ----
/src/feature/           @org/core-team
/src/service/           @org/core-team

# ---- HIGH: 핵심 도메인 / 데이터 (Section 9.1 HIGH 패턴) ----
/src/core/              @org/senior-devs
/src/domain/            @org/domain-experts @org/senior-devs
/src/api/               @org/api-owners
/db/                    @org/data-team @org/senior-devs
/migrations/            @org/data-team @org/senior-devs

# ---- 인프라/CI ----
/infrastructure/        @org/sre-team
/.github/               @org/devops-team

# ---- CRITICAL: 보안/결제/규제 (Section 9.1 CRITICAL 패턴) ----
/src/auth/              @org/security-team @org/senior-devs
/src/security/          @org/security-team
/src/payment/           @org/security-team @org/payment-team
/src/pii/               @org/security-team @org/privacy-team

# ---- CODEOWNERS 자체 보호 (권한 상승 방지) ----
/.github/CODEOWNERS     @org/security-team @org/tech-leads
```

---

## 4. 작성 원칙

1. **Risk와 정렬**: CRITICAL 경로(Section 9.1)에는 반드시 보안팀 포함 → TIER 1의 EXPERTISE 비트와 일치
2. **팀 단위 지정**: 개인 지정은 휴가/퇴사 시 병목(SPOF). 팀으로 지정하고 팀 내부에서 로테이션
3. **과도한 지정 금지**: 모든 경로를 촘촘히 지정하면 리뷰 부하 폭증. fallback + 민감 경로만으로 시작
4. **CODEOWNERS 자체 보호**: 이 파일을 수정해 리뷰를 우회하는 것을 막기 위해 파일 자체에 소유자 지정
5. **와일드카드 순서 주의**: `*.md`를 마지막에 두면 `/src/auth/README.md`가 docs-team에게만 가는 사고 발생 — 민감 경로를 항상 아래에

---

## 5. 운영 체크리스트

```markdown
## CODEOWNERS 운영 점검 (분기 1회)
- [ ] 스테일 오너 점검 (퇴사자, 팀 변경, 비활성 팀)
- [ ] 리뷰어 부하 확인 (Review_Pipeline_Guide.md Section 13.1 리뷰어 부하 메트릭)
- [ ] 신규 주요 디렉토리에 소유자 누락 없는지 확인
- [ ] CRITICAL 경로 커버리지 확인 (Section 9.1 패턴 대비)
```

---

## 6. 강제화 (Phase 2 예고)

CODEOWNERS만으로는 "자동 할당"까지만 됩니다. **승인 강제**는 다음 설정이 필요합니다:

- **GitHub**: Branch Protection → "Require review from Code Owners" 활성화
- **GitLab**: Protected Branches + "Code Owner approval required"

상세 설정은 Phase 2의 `BranchProtection_Guide.md`(TO-BE.md P2-4)에서 다룹니다.
