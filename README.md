# Code Review Pipeline

AI 기반 코드 리뷰를 위한 가이드라인 및 분류 체계 레포지토리입니다.

## 개요

이 레포지토리는 **서브 레포**로서 메인 프로젝트에 복사되어 내부 코드 리뷰 프로세스로 작동할 수 있도록 설계되었습니다. Claude AI가 코드 리뷰 수행 시 참조하는 상세한 가이드맵을 제공합니다.

**주요 기능**:
- 코드 자동 분류 (Risk, Size, Domain, Type, Sensitivity)
- 분류 기반 리뷰 Tier 결정 (1~4)
- Tier별 체크리스트 기반 리뷰 수행
- **완성도 리포트 생성** (운영 가능 수준 판단)

## 구조

```
code_review/
├── CLAUDE.md                              # 코드 리뷰 파이프라인 가이드 (핵심 문서)
├── README.md                              # 레포지토리 설명
├── LICENSE
├── __Prompt/                              # 실행 프롬프트
│   ├── Code_Review_Execution.md           # 코드 리뷰 실행 가이드
│   ├── Report_Template.md                 # 완성도 리포트 템플릿
│   ├── Quick_Start.md                     # 빠른 시작 가이드
│   └── Scenario_Creation_Guide.md         # 시나리오 생성 가이드
├── research/                              # 리서치 자료
│   ├── classification.md                  # 분류 체계 이론
│   └── backend_cleancode.md               # 실무 트리아지 체계
└── _Visualization/                        # 시각화 보조 자료
```

## 핵심 문서

### CLAUDE.md

Claude AI가 코드 리뷰 수행 시 따라야 할 상세한 가이드 문서입니다.

주요 내용:
- **Quick Start**: 4단계 코드 리뷰 플로우 (CLASSIFY → DEPTH → REVIEW → OUTPUT)
- **분류 체계**: 위험도, 규모, 도메인, 변경 유형, 규제/보안 민감도
- **리뷰 깊이 매트릭스**: Tier 1~4 결정 로직 및 요구사항
- **체크리스트**: 공통, Tier별, 변경 유형별 체크리스트
- **출력 형식**: 표준화된 리뷰 결과 템플릿
- **에스컬레이션**: 불확실한 상황에서의 처리 경로
- **자동 분류 기준**: 경로/키워드 기반 분류 규칙
- **완성도 평가 기준**: 영역별 점수 산정 및 전체 평가 기준

### __Prompt/

코드 리뷰 실행을 위한 프롬프트 및 템플릿입니다.

| 파일 | 용도 |
|------|------|
| `Code_Review_Execution.md` | 코드 리뷰 실행 가이드 (분류 → 리뷰 → 리포트) |
| `Report_Template.md` | 완성도 리포트 템플릿 (복사해서 사용) |
| `Quick_Start.md` | 빠른 시작 가이드 (설치, 사용법, FAQ) |

### research/

코드 리뷰 분류 체계의 이론적 배경과 산업계 베스트 프랙티스를 정리한 리서치 문서입니다.

## 사용 방법

### 1. 서브 레포로 복사

메인 프로젝트에 이 레포지토리를 서브 디렉토리로 복사합니다.

```bash
# 방법 1: Git subtree
git subtree add --prefix=code_review <repository-url> main --squash

# 방법 2: 단순 복사
cp -r code_review/ /path/to/main-project/
```

### 2. 코드 리뷰 요청

Claude에게 다음과 같이 요청합니다:

```
code_review/CLAUDE.md를 참조하여 다음 코드를 리뷰해줘:

## 리뷰 대상
- 파일: src/payment/checkout.py
- 변경 목적: 결제 실패 시 재시도 로직 추가

## 코드
[코드 블록 또는 git diff]

완성도 리포트까지 생성해줘.
```

### 3. 예상 출력

Claude는 다음과 같은 형식으로 리뷰 결과를 제공합니다:

```markdown
# 코드 리뷰 완성도 리포트

## 1. 분류 요약
| 항목 | 값 |
|------|-----|
| Risk Level | HIGH |
| Size | M (150줄) |
| Domain | Core |
| Change Type | Perfective |
| Sensitivity | PCI-DSS |
| Review Tier | TIER 1 |

## 2. 완성도 평가
### 전체 평가: NEEDS_WORK
### 완성도 점수: 68/100

| 영역 | 점수 | 상태 |
|------|------|------|
| 기능 완성도 | 20/25 | ⚠️ |
| 코드 품질 | 18/25 | ⚠️ |
| 테스트 커버리지 | 15/25 | ⚠️ |
| 보안/안정성 | 15/25 | ⚠️ |

## 3. 발견 사항
### Critical
1. [Security] 결제 금액 검증 누락 - `processor.py:45`
...

## 4. 운영 가능성 판단
**결론**: 아니오
**필수 수정 사항**: ...
```

### 4. 커스터마이징

조직에 맞게 다음 항목을 수정합니다:
- 에스컬레이션 연락처 (CLAUDE.md Section 7.3)
- 규제/보안 분류 기준 (CLAUDE.md Section 2.5)
- 자동 분류 경로 패턴 (CLAUDE.md Section 9)
- 자동화 연계 포인트 (CLAUDE.md Section 8.3)

> 상세한 사용법은 `__Prompt/Quick_Start.md`를 참조하세요.

## 분류 체계 요약

| 분류 축 | 내용 | 출처 |
|---------|------|------|
| 위험도 기반 | CRITICAL/HIGH/MEDIUM/LOW | backend_cleancode.md 2.1 |
| 도메인 기반 | Core/Supporting/Generic | classification.md 3.1 |
| 변경 유형 | Corrective/Adaptive/Perfective/Preventive | classification.md 4.1 |
| 복잡도 기반 | 인지 복잡도, 순환 복잡도, 결합도 | classification.md 5.1-5.2 |

## 리뷰 Tier 요약

| Tier | 깊이 | 리뷰어 |
|------|------|--------|
| TIER 1 | Full Deep | 시니어 2인 + 전문팀 |
| TIER 2 | Comprehensive | 시니어 1인 + 도메인 전문가 |
| TIER 3 | Standard | 1인 리뷰 |
| TIER 4 | Light | 자동화 체크 |

## 언어

- 문서: 한국어
- 코드 예시: 언어 무관

## 라이선스

[LICENSE](LICENSE) 파일을 참조하세요.
