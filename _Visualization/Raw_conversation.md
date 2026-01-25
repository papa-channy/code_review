지금부터 너랑 나랑은 서비스 기획자로서 엔터프라이즈 서비스를 어떻게 설계할지 같이 논의할거고 너는 나에게 내가 제시한 내용에 대해 잘 정리하고 개선 포인트나 고려사항에 대해 조언을 해주는 역할을 맡으면 돼 준비됐어?

응, 바로 시작하자.

내 역할은 이렇게 가져갈게:

네가 던진 아이디어/요구사항을 서비스 기획 관점에서 구조화(목표→유저→문제→해결→정책/운영→리스크) 해서 정리

바로 믿지 않고 “이 가정이 맞나?” “이건 누가 돈 내지?” “운영이 되나?” “보안/권한/감사 로그는?” 같은 식으로 의심하면서 빈틈 찌르기

개선 포인트는 우선순위/범위조정(MVP vs 확장), 엔터프라이즈 필수요건(SSO, RBAC, Audit, SLA, Admin, Compliance) 중심으로 제안

바로 다음 메시지에 아래 6가지만 써줘. 길게 안 써도 돼. (대충이라도 주면 내가 그걸 기반으로 정리/강화할게)

서비스 한 줄 정의: “우리는 ___을(를) ___에게 ___하게 해주는 서비스”

타깃 회사/팀: (예: 제조 R&D, 병원, SaaS 개발조직 등)

핵심 유스케이스 3개: 사용자가 실제로 하는 행동 단위

데이터/연동: 어떤 시스템(Drive/Slack/Jira/GitHub 등)과 붙는지 + 민감도

과금 주체/모델 가설: 누가 결제하고 왜 유지할지

성공 지표: 도입 후 뭐가 줄거나 늘면 성공인지

이걸 주면, 내가 요구사항 문서 형태로 재구성하고, 동시에 “엔터프라이즈에서 반드시 터지는 지점”(권한, 감사, 온보딩, 운영, 보안, 정책, 책임경계)을 체크리스트로 뽑아서 다음 단계로 밀어줄게.

우선 우리 서비스에 대해 소개하자면 Snowflake나 Palantir와 비슷하지만 좀 더 실무자들에게 fit하게 “AI”와 “개인 아이디어 및 문서 데이터”, “회사 데이터”를 연결시켜 생산성을 높이는 워크스페이스 툴이라고 생각해면 되고
지금 우리가 논의할 내용은 이 서비스에 들어갈 여러 서비스 레이어의 기능에 대한 논의는 전혀 아니고(얘기 x)
우리가 각 회사의 보안 이슈와 데이터 소유에 대한 해결책으로서 라이센스형 온프레미스 구조로 설계를 해놓은 상태(이건 불변)이고 구조적으로 “내”가 운영하는 중앙 서버가 존재하고 “각 회사”가 운영하는 내부 서버가 존재하는거야
이제 여기서 나랑 논의하며 결정할 부분은 개인사용자와 엔터프라이즈 사용자의 회원가입 시작부터 “각 회사” 서버 온보딩 + 초기 tenant관리자 계정 생성 방식, tenant 관리자 페이지 설계, 내부 데이터  격리 구조(이미 고려한게 있지만 좀 더 고도화 예정) 그리고 엔터프라이즈 사용자의 회사 퇴사 시 데이터 처리 방식에 대한 내용이야
일단 논의는 순차적으로 하나씩 정리하면서 갈거고 우선 너가 알아야할 사항은 n:n방식으로 하나의 계정에 개인 프로필/회사 프로필 처리를 할거라는거?
이제 시작해보자
18s 동안 생각함

좋아. 근데 지금 네 설명에는 “헷갈리면 그대로 사고 나는 지점”이 몇 개 있어서, 기능 얘기 없이도 용어/경계/권한부터 못 박고 들어가는 게 맞아. (안 그러면 회원가입/온보딩/퇴사 처리에서 정책 충돌이 나옴)

아래는 불변 조건 요약 → 우리가 설계해야 할 핵심 객체 모델 → 가입/온보딩의 표준 플로우(권장안) 순서로 정리할게. 그리고 여기서부터 순차적으로 확정해가자.

0) 불변 조건(내가 이해한 그대로)

배포 형태: 라이선스형 온프레미스(회사 내부 서버) 는 고정.

구조: 중앙 서버(너가 운영) + 각 회사 내부 서버(테넌트가 운영) 공존.

논의 범위:

개인/엔터 회원가입 시작

회사 서버 온보딩 + 초기 tenant admin 생성

tenant admin 페이지 설계

내부 데이터 격리 구조 고도화

퇴사 시 데이터 처리

계정 모델: n:n (한 계정이 개인 프로필 + 여러 회사 프로필을 가질 수 있음)

여기까지 OK.

1) 먼저 “객체 모델”을 안 박으면 전부 흔들림 (최소 정의)

기능 얘기 말고 데이터 소유/권한/식별만 정의하자.

핵심 엔티티(추천 최소 세트)

Account (Global User): 중앙 서버에 존재하는 “사람” 단위 계정

Personal Profile: Account의 개인 영역(개인 데이터/설정)

Tenant (Company): 회사 단위(법인/조직)

Membership: Account ↔ Tenant 연결(N:N) + 상태(Active/Suspended/Terminated)

Role Binding: Membership에 부여되는 권한(예: Tenant Admin, Security Admin, Member)

On-prem Server (Tenant Data Plane): 테넌트 내부 서버 인스턴스(여러 대 가능)

Identity Link: SSO/IdP로 들어온 외부 ID와 Account 매핑(이거 없으면 퇴사/접근통제가 망가짐)

Data Boundary: Personal vs Tenant 데이터 경계(소유권/보존/삭제 정책 포함)

이 모델로 가면, “계정 1개로 개인+회사 여러 개”가 자연스럽게 처리됨.

2) 가입/온보딩에서 제일 먼저 결정해야 하는 2가지 (안 정하면 계속 꼬임)
결정 A. 엔터프라이즈 로그인 방식

옵션 A1: 중앙 Account 기반 + SSO 연동(권장)

사용자는 중앙 계정이 있고, 회사는 SSO로 인증하되 중앙 계정에 매핑

장점: 개인/회사 프로필 공존이 깔끔, 여러 회사 N:N 가능, 중앙에서 장치/세션 정책 가능

단점: “중앙 서버에 사용자 식별자가 존재”하는 걸 싫어하는 기업이 있음(메일/이름 최소화 필요)

옵션 A2: 회사 SSO만으로 로그인(계정은 테넌트 내부에서만)

장점: 중앙에 사용자 식별정보를 거의 안 둠

단점: 개인 프로필/다중 회사(N:N) 모델이 지옥이 됨(연결 계정/이관/퇴사 처리 복잡)

너는 이미 “개인+회사 n:n”을 전제로 했으니, 현실적으로 A1이 맞아.

결정 B. 온프레미스 서버가 중앙 서버와 통신 가능한가?

옵션 B1: Outbound 가능(중앙 control-plane에 등록)

옵션 B2: Air-gapped(오프라인 라이선스/수동 등록)

이건 기업 세일즈에서 무조건 부딪혀. 둘 다 지원 안 하면 시장이 확 줄어.

3) 권장 “표준 플로우 3종” (여기서부터 순차적으로 확정하자)
플로우 1) 개인 사용자 시작

중앙 서버에서 Account 생성(Email/Passkey 등)

Personal Profile 자동 생성

기본 상태: Tenant 없음

→ 여기서 논쟁거리 없음.

플로우 2) 기존 회사(Tenant)에 합류 (직원이 들어오는 케이스)

입장 경로를 2개로 두는 게 안전함.

(2-1) SSO로 첫 로그인

회사 IdP(SSO)로 로그인

중앙 서버에서 Identity Link 확인

없으면: “해당 도메인/IdP에 연결된 Tenant”를 찾아서 Membership 생성

Role은 기본 Member, 필요한 경우 그룹 매핑으로 Role 부여(SCIM 연동은 나중)

(2-2) 초대 링크(Invite)로 합류

보안상 Invite는 “이메일 소유 확인 + 만료 + 1회성 토큰” 필수

SSO를 강제할지(엔터 기본) 여부도 정책으로 가능

→ 핵심은 “사용자 계정 생성”과 “테넌트 멤버십 생성”을 분리하는 것. 그래야 n:n이 자연스럽다.

플로우 3) 회사(Tenant) 신규 생성 + 온프레미스 서버 온보딩 + 첫 Admin 만들기

여기서 사고가 제일 많이 난다. 내가 권장하는 건 2단계 부트스트랩이야.

3-A) Tenant 생성(중앙 control-plane)

“Tenant 생성 요청자”가 중앙에서 Tenant를 만든다

중앙에서 Tenant Bootstrap Token 발급 (짧은 TTL, 1회성)

이 시점엔 아직 on-prem 서버 없음

3-B) On-prem 서버 등록(테넌트 data-plane 온보딩)

서버 설치 후 첫 실행에서:

서버가 키페어 생성 → CSR 생성

Bootstrap Token으로 중앙에 등록 요청

중앙이 Tenant에 연결된 “Server Identity Certificate” 발급

이후 통신은 mTLS + 서버 지문 pinning 같은 형태로 고정

중앙은 “서버 등록됨” 상태만 관리 (실데이터는 테넌트에 남음)

Air-gapped면: 중앙에서 등록 파일(license+cert bundle) 내려받아 수동 반입하는 루트도 필요.

3-C) 초기 Tenant Admin 계정 생성(여기 방식 선택이 중요)

여기서 선택지가 크게 2개야.

방식 C1: “초기 Admin은 중앙 계정(사람)으로 지정” (권장)

Tenant 생성자가 곧 Admin

장점: 중앙에서 감사/정책/권한 부여 일관성

단점: 중앙에 사람 식별이 남는 걸 싫어하는 고객이 있을 수 있음(최소화 설계로 해결)

방식 C2: “온프레미스 로컬 Break-glass Admin 1개를 먼저 만든다”

설치 중 로컬에서 admin 생성 → 이후 SSO로 사용자 동기화

장점: 중앙 의존 최소

단점: 운영상 위험(공유 계정/비밀번호/퇴사 처리/감사 구멍)

내 결론: 둘 다 제공하되, 기본은 C1 + C2는 ‘Emergency only’로 격리가 맞다.
(엔터프라이즈는 결국 Break-glass 요구하는 경우가 많음)

4) 지금 단계에서 “너가 이미 고려했다는 격리 구조”가 불완전해지기 쉬운 지점

아직 격리 설계 세부는 다음 순서에서 다루되, 가입/온보딩과 연결되는 최소 체크만 박아둘게.

개인 데이터 vs 회사 데이터는 소유권이 다르다 → 저장소/키/삭제 정책도 달라야 함

같은 문서라도 “개인이 만든 뒤 회사에 가져간 것”이 발생함
→ “복사본”인지 “공유(소유권 이전/공동소유)”인지 정책이 필요
(퇴사 시 여기서 소송 난다)

5) 다음 스텝: 오늘은 “첫 결정”부터 박자

지금 당장 확정해야 다음 논의가 안 흔들리는 질문은 딱 2개뿐이야. (짧게 답해도 됨)

엔터프라이즈 인증은 중앙 Account + SSO 매핑(A1) 로 간다 (YES/NO)

온프레미스 서버는 Outbound 통신 가능(B1) 을 기본으로 두되, Air-gapped(B2) 옵션도 지원한다 (YES/NO)

너가 여기만 찍어주면, 다음 턴에서

“Tenant admin 생성 방식(C1/C2 정책)”을 확정하고

그걸 기준으로 tenant admin 페이지 IA(Information Architecture) 를 “계정/권한/감사/서버상태/보존정책” 관점에서 바로 설계로 들어갈게.

A1이 맞고 우리는 해당 고객이 각 회사별 프로필의 존재여부만 확인하고, 그 프로필의 데이터는 모두 각 회사 내부 서버에 저장되는거 아닌가?
결정 B는 용어를 이해 못했어 더 풀어서 설명해주고
플로우2에서 내 생각은 다른게 “내”서버 즉 공용 서버는 연동로그인으로 하고
각 tenant admin계정에서 초대를 보내거나 계정에서 각 회사 계정으로 sso 로그인 이후 tenant 관리자 승인 요청 보내는 두 방법 모두 지원을 생각했는데 
여기까지 결정 짓고 플로우3은 더 상세하게 다시 논의하자

좋아. 지금 네가 말한 방향(A1 + “중앙은 존재 여부만, 데이터는 전부 테넌트 내부”)은 큰 그림은 맞는데, “중앙에 아무것도 없다”로 오해하면 바로 터져. 중앙이 최소한으로 들고 있어야 하는 메타데이터/권한/감사가 있다. 그 경계를 먼저 깔끔히 정의하자.

1) A1에서 “중앙은 프로필 존재 여부만”이 가능한가?

가능한데, 정확히는 이렇게 정리해야 안전해.

중앙 서버(너 운영)가 반드시 들고 있어야 하는 것(최소 세트)

Account(사람) 식별자: email/phone/passkey 등 (SSO 매핑을 위해 필요)

Tenant ‘존재’ 및 연결 정보: tenant_id, tenant_name(또는 익명표시), tenant의 IdP/도메인 매핑

Membership(소속 관계): account_id ↔ tenant_id + 상태(pending/active/terminated 등)

Role(권한 바인딩): 최소 “Tenant Admin 여부”는 중앙에 있어야 함 (승인/접근통제)

On-prem 서버 등록 정보: 서버 지문, 인증서, 상태(online/offline), 라이선스 상태

감사 로그(컨트롤플레인 레벨): “누가 언제 어떤 테넌트에 가입/승인/권한변경/서버등록” 같은 이벤트

👉 반대로, 네가 말한 “각 회사 프로필 데이터”는 아래로 내려가야 함.

테넌트 내부 서버(회사 운영)에만 있어야 하는 것

회사 프로필의 실데이터 전부: 문서/아이디어/임베딩/검색인덱스/워크스페이스 설정/회사 내부 계정 메타(부서 등)

회사 내부 감사 로그(데이터플레인): 문서 열람/다운로드/공유/내보내기 같은 행위

핵심: 중앙은 “접속권한과 연결만” 관리하는 Control-plane, 테넌트 서버는 “실데이터” 관리하는 Data-plane.

그리고 여기서 회의적으로 한 마디:
중앙이 “테넌트 존재 여부”를 보여주는 순간 테넌트 열거(회사 존재 노출) 리스크가 생겨.
→ 그래서 UI/응답에서 “이메일 도메인으로 테넌트 추정” 같은 건 제한하거나, SSO 리디렉션 기반으로만 노출되게 해야 한다.

2) 결정 B (Outbound / Air-gapped) 쉽게 설명

내가 말한 B는 “테넌트 내부 서버가 중앙 서버랑 네트워크로 통신 가능한 환경인지”야.

B1. Outbound 가능(대부분 기업이 이 형태)

회사 내부 서버가 바깥(인터넷/중앙서버)으로 나가는 통신(HTTPS) 은 허용

인바운드(외부→회사 내부로 들어오는 연결)는 막혀있을 수 있음 (대부분 막음)

이 경우 설계는 보통 테넌트 서버가 중앙으로 ‘등록/하트비트/라이선스 검증’을 주기적으로 호출하는 모델이 된다.

예) 내부 서버 → 중앙 서버로

“나 살아있음(heartbeat)”

“라이선스 유효함?”

“업데이트/정책 변경 있음?”

“사용자 승인 상태 동기화 필요?”

B2. Air-gapped(완전 격리망/폐쇄망)

회사 내부 서버가 외부 인터넷과 아예 통신 불가

이 경우 중앙이 실시간으로 뭘 해줄 수가 없음

대신 오프라인 라이선스 파일/서명된 번들을 사람이 USB 등으로 옮기는 방식이 필요

왜 이게 중요하냐?
B1이면 “가입/권한/라이선스/서버상태”가 중앙에서 비교적 잘 관리돼.
B2면 모든 게 “오프라인 절차”가 되기 때문에 온보딩/퇴사/권한변경이 다 느려지고 복잡해짐.

지금 단계에서 네가 결정을 못 하겠다면, 최소 이렇게는 말할 수 있어:

기본은 B1(Outbound)

큰 고객을 위해 B2(Offline bundle) 을 “엔터프라이즈 옵션”으로 열어둔다

3) 플로우2: 네가 제안한 “초대 + 승인요청” 방식, 맞음. 다만 상태 머신으로 박아야 함

네가 말한 두 경로를 “같은 상태 머신”으로 합쳐야 운영/보안이 깔끔해져.

플로우2-A: Tenant Admin이 초대(Invite)

Admin이 중앙(또는 테넌트 관리 UI)을 통해 invite 발송

사용자는 중앙 로그인(연동 로그인)

Membership 생성: invited → 사용자가 수락하면 pending_active 또는 바로 active (정책에 따라)

플로우2-B: 사용자가 SSO 로그인 후 “승인 요청”

사용자가 회사 SSO로 로그인

중앙에서 IdP/도메인으로 Tenant 식별

Membership 생성: pending_approval

Tenant Admin이 승인하면 active

여기서 반드시 필요한 장치:

“SSO 로그인만 했다고 자동 active”는 위험함(외주/협력사/도메인 유사 등).
→ 기본은 pending_approval, 예외로 “자동 승인 그룹/SCIM” 같은 걸 기업이 원할 때만.

초대 링크는 만료 + 1회성 + 이메일 검증 필수.

중앙이 tenant 존재를 노출하지 않도록
→ “이 도메인에 테넌트가 있습니다” 같은 응답은 조심해야 함. 보통은 SSO 리디렉션 기반으로만 자연스럽게 유도.

Membership 상태(추천)

invited

pending_approval

active

suspended (보안/정책 위반)

terminated (퇴사/계약 종료)

left (자진 탈퇴)

이걸 확정하면, 다음에 “퇴사 시 데이터 처리”도 정확히 걸 수 있어.

4) 여기까지 “결정”으로 박자 (내가 정리한 확정안)

A1: 중앙 Account + SSO 매핑 확정

중앙은 Control-plane 최소 메타데이터만 저장, 회사 데이터는 Data-plane(온프레미스) 저장

플로우2는 Invite + SSO 후 승인요청 둘 다 지원

Membership은 상태 머신 기반으로 통일

5) 다음 논의(플로우3)로 넘어가기 전에, 딱 1개만 더 고정하자

플로우3 상세 들어가려면 이것부터 고정해야 한다.

테넌트 “식별”의 기준을 뭘로 할래?

(안1) IdP 연결(SSO 설정) 이 테넌트의 유일한 식별자 (가장 안전)

(안2) 이메일 도메인 기반 (편하지만 위험/예외 많음)

(안3) 둘 다: 도메인은 힌트, 최종은 IdP

나는 (안3)로 가되, 최종 매칭은 IdP로 고정하는 걸 권장해. 도메인만 믿으면 사고 난다.

너는 여기서 어떤 걸로 갈래?
(이거 한 줄로 답하면, 바로 플로우3 “온프레미스 서버 온보딩 + 최초 admin 생성” 상세 설계로 들어갈게.)

여기서 궁금한게 라이센스가 종료된 경우  우리 서비스를 못쓰게 해야하잖아?
그때 우리 라이센스 서버 안에 존재하던 데이터는 어떻게해야해?

맞아. 라이선스 종료 = 서비스를 못 쓰게 해야 함은 맞는데, 여기서 “못 쓴다”를 어떻게 정의하느냐에 따라 데이터 처리 정책이 완전히 갈려. 특히 너희 구조(중앙 라이선스/컨트롤 서버 + 고객 온프레미스 데이터 서버)에서는 중앙에 있는 데이터와 테넌트 내부 데이터는 분리해서 다뤄야 해.

1) 먼저 전제: 중앙(라이선스 서버)에 “무슨 데이터가 있나?”

너희가 아까 말한 방향대로라면 중앙에 남는 건 대략 이거뿐이야.

account_id, 최소 PII(email 등)

tenant 존재/연결 정보(tenant_id, IdP 설정)

membership/role(누가 어떤 테넌트에 속했는지)

서버 등록 정보(인증서/지문/상태)

컨트롤플레인 감사 로그(승인/권한변경/서버등록 같은 이벤트)

즉, 중앙에 “문서/아이디어/회사 데이터”가 있으면 그건 이미 설계가 새고 있는 거고, 중앙은 원칙적으로 메타데이터만 있어야 함.

2) 라이선스 종료 시 “중앙 서버 데이터” 처리 옵션 3가지

여기서 가장 흔한 함정: “종료하자마자 전부 삭제”는 기업 입장에서도 위험해(분쟁/감사/정산). 반대로 “계속 보관”도 개인정보/규정 리스크.

옵션 A: 즉시 차단 + 보관(유예) + 자동 삭제 (권장)

T=만료 즉시

중앙: 모든 토큰/세션 revoke, tenant를 license_expired 상태로 전환

새 로그인/승인/권한변경/서버등록 차단

Grace period (예: 30~90일)

목적: 갱신/정산/분쟁 대응

중앙 데이터는 “관리/복구를 위한 최소”만 유지

유예 종료 후

중앙에 있는 tenant 관련 메타데이터를 정책에 따라 삭제/익명화

단, 회계/법적 증빙이 필요한 최소 항목은 계약서에 근거해 별도 보존(예: 청구 기록)

이게 가장 “엔터프라이즈랑 싸움이 덜 나는” 기본값이야.

옵션 B: 즉시 전부 삭제(강경)

보안적으로는 깔끔하지만,

고객이 “실수로 갱신 못했는데 모든 연결/관리 정보 날아감” 같은 이슈가 생기면 바로 클레임.

옵션 C: 무기한 보관(위험)

개인정보/컴플라이언스에서 지뢰밭. 특히 퇴사자/탈퇴자 데이터까지 섞이면 더 위험.

3) 그럼 “고객 온프레미스 서버(회사 내부)에 있는 데이터”는?

여기가 핵심이야. 서비스를 못 쓰게 하는 것이 곧 데이터를 삭제하는 것은 아니야.

보통 B2B 온프레미스는 이렇게 간다:

권장 정책: “사용 불가(기능 잠금) + 데이터는 고객이 소유”

라이선스 만료 시 온프레미스 서버는 쓰기/검색/에이전트 실행 같은 핵심 기능을 잠금

대신 최소한:

데이터 Export(반출) / 백업 다운로드

읽기 전용 보기

관리자 화면에서 ‘완전 삭제’ 버튼(고객이 선택)
같은 “종료 절차”는 제공하는 게 분쟁이 적어.

고객 데이터는 고객이 소유인데, 만료했다고 너희가 원격으로 “회사 내부 데이터 삭제”를 강제하면 법무/영업에서 터지는 경우가 많아.

4) 기술적으로 만료를 “강제”하려면 (중앙/온프레미스 각각)

너희 구조에 맞춰 2개로 나뉜다.

(1) 중앙 서버 기반(B1: outbound 가능)일 때

온프레미스 서버가 주기적으로 중앙에 “라이선스 유효?” 체크

만료면 중앙이 deny → 온프레미스는 잠금 모드 진입

(2) 완전 폐쇄망(B2: air-gapped)일 때

중앙 체크가 안 되니까 오프라인 라이선스 파일(서명된 토큰) 이 필요

파일에 만료일/권한이 포함되고, 온프레미스는 그걸 검증

여기서 현실 이슈: 서버 시간 조작(clock rollback) 방어를 고민해야 함
(완벽 방어는 어렵고, 탐지/운영정책으로 커버하는 경우가 많음)

5) 너 질문에 대한 “답”을 한 줄로 정리하면

라이선스 종료 시 중앙(라이선스 서버) 에 남아있는 건 “접속/소속/권한/서버등록 같은 최소 메타데이터”뿐이어야 하고,
만료 즉시 접근은 차단하되 계약에 명시한 유예기간 후 자동 삭제/익명화로 가는 게 가장 현실적이야.
고객 온프레미스에 있는 회사 데이터는 잠금(사용불가) 처리가 원칙이고, 삭제는 고객이 선택하도록.

다음 단계로 바로 결정하자 (플로우3 들어가기 전에 필수)

라이선스 종료 정책에서 딱 3개만 정하면 설계가 진행돼:

Grace period 기간: 0일 / 30일 / 90일 중 뭐로 기본값?

만료 상태에서 온프레미스는 완전 잠금 vs Read-only+Export 허용 중 뭐?

중앙 메타데이터는 유예 후 완전 삭제 vs 익명화 보존(감사/청구 최소) 중 뭐?

너가 이 3개를 찍어주면, 그걸 전제로 플로우3(온보딩/초기 admin 생성/테넌트 관리 페이지)의 정책과 UX를 끊김 없이 설계로 들어갈 수 있어.

혹시 이 내용에 대해서 좀 더 다른사람들도 이해가 가능하도록 도식화해줄래?

좋아. 아래는 “이걸 처음 보는 사람”도 이해하도록 3장짜리 도식(아키텍처 / 데이터 위치 / 라이선스 종료 시 흐름) 으로 정리한 거야. (용어도 같이 고정)

1) 전체 구조 도식: Control-plane(중앙) vs Data-plane(회사)
flowchart LR
  U[User] -->|Login| CP[Central Server<br/>(Control-plane / License)]
  CP -->|SSO Redirect / Identity Link| IdP[Company IdP<br/>(SSO)]
  IdP -->|SAML/OIDC| CP

  CP <--> |mTLS (Outbound from on-prem)| DP[Tenant On-prem Server<br/>(Data-plane)]
  DP --> DS[(Company Data Store<br/>Docs / Ideas / Index / Embeddings)]
  
  CP --> CM[(Control Metadata Store<br/>Accounts / Membership / Roles<br/>Server registry / License state<br/>Control-plane audit log)]


핵심 한 줄

중앙(CP): “누가 어떤 회사에 속하는지 / 권한 / 라이선스 / 서버 등록 상태”만 가짐

회사(DP): “실제 문서/아이디어/회사 데이터” 전부 가짐

2) 데이터가 어디에 저장되는가(경계선 도식)
flowchart TB
  subgraph Central["Central Server (Control-plane)"]
    A1[Account ID / Minimal PII<br/>(email, passkey id)]
    A2[Tenant Registry<br/>(tenant_id, IdP config)]
    A3[Membership / Role Binding<br/>(active, pending, terminated)]
    A4[Server Registry<br/>(cert fingerprint, status)]
    A5[License State<br/>(active, expired, grace)]
    A6[Audit (Control Events)<br/>(invite/approve/role change)]
  end

  subgraph Tenant["Tenant On-prem (Data-plane)"]
    B1[Workspace Data<br/>(Docs, Ideas, Files)]
    B2[Index & Embeddings<br/>(Search/Vector)]
    B3[Tenant Settings<br/>(Policies, retention)]
    B4[Audit (Data Events)<br/>(open/export/share)]
    B5[Internal User Attributes<br/>(dept, org chart etc.)]
  end

  Central --- Tenant


이 도식이 말하는 것

중앙은 “프로필 존재 여부” 수준의 메타데이터만

“회사 데이터”는 무조건 테넌트 내부에만

3) 라이선스 종료 시 ‘무엇이 어떻게 잠기는가’ 흐름 도식
3-A) Outbound 가능한 경우(B1) — 일반적인 온프레미스
sequenceDiagram
  participant DP as Tenant On-prem (Data-plane)
  participant CP as Central (Control-plane / License)
  participant U as User

  DP->>CP: License check (heartbeat)
  CP-->>DP: OK (ACTIVE)

  Note over CP,DP: License expires
  DP->>CP: License check (heartbeat)
  CP-->>DP: DENY (EXPIRED)

  DP-->>U: Enter "LOCKED MODE"
  Note over DP,U: Block: write/search/AI actions<br/>Allow(optional): read-only + export


결론

만료 즉시 중앙이 DENY를 주면, 온프레미스가 Lock mode로 들어감

“삭제”가 아니라 “사용불가(잠금)”이 기본

3-B) Air-gapped(B2) — 완전 폐쇄망(옵션)
sequenceDiagram
  participant Admin as Tenant Admin (Human)
  participant CP as Central (License Issuer)
  participant DP as Tenant On-prem (Offline)

  Admin->>CP: Request offline license bundle
  CP-->>Admin: Signed license file (expires at T)
  Admin->>DP: Import license file
  DP-->>DP: Verify signature + expiry

  Note over DP: When expired -> LOCKED MODE


결론

중앙과 실시간 통신이 없으니 서명된 오프라인 라이선스 파일로 만료를 강제

4) 중앙 서버(라이선스 서버)에 남아있는 데이터는 만료 시 어떻게 되나?
stateDiagram-v2
  [*] --> ACTIVE
  ACTIVE --> EXPIRED: License end date reached
  EXPIRED --> GRACE: Grace period enabled
  GRACE --> DELETED: After N days (policy)
  EXPIRED --> DELETED: If no grace

  state ACTIVE {
    [*] --> FullAccess
  }
  state EXPIRED {
    [*] --> BlockNewAuth
  }
  state GRACE {
    [*] --> MinimalRetention
  }
  state DELETED {
    [*] --> PurgedOrAnonymized
  }


정책 의미

ACTIVE: 정상

EXPIRED: 로그인/승인/권한변경 등 컨트롤플레인 작업 차단

GRACE: 정산/분쟁 대비를 위해 “최소 메타데이터”만 보관

DELETED: 테넌트 관련 중앙 메타데이터 삭제(또는 익명화)

5) 같은 그림을 “한 문장”으로 요약하면

데이터는 회사 안에 남고,

라이선스가 끝나면 기능이 잠기며,

중앙 서버엔 연결/권한/라이선스 같은 최소 메타만 유예 후 삭제/익명화한다.

원하면 내가 이 도식을 기반으로, 내부 문서에 바로 넣을 수 있게:

“용어 사전(Glossary)”

“라이선스 만료 정책 표(옵션별 장단점)”

“Lock mode에서 허용 기능(예: Export 허용 여부) 체크리스트”
까지 1페이지짜리로 딱 정리해줄게.

지금 내가 필요한건 흐름도인데
4개의 집단으로 구분할거야
1. 우리
2. B2B 고객 서버
3. B2B 사용자
4. 일반 사용자

여기서 더 세분화해서
1-1은 우리 라이센스 관리 서버
1-2는 우리 일반 사용자용 서버

이 때 4(일반 사용자)의 회원가입부터 탈퇴까지의 플로우 및 고려사항 체크리스트
3의 회원가입(일반 회원가입 -> 사내 서버 등록)부터 퇴사(데이터 처리)까지 플로우
2의 우리와 계약부터 tenant server 인증 허가 등록 설치 사용 라이선스 만료 사용 종료 시나리오까지

이걸 초안을 그려줄래
12s 동안 생각함

아래는 “초안(flowchart draft)” 수준으로 바로 문서에 붙일 수 있게, 너가 말한 4개 집단 + (1-1/1-2 분리) 기준으로 3개의 흐름도를 그린 거야.
(일부 정책은 “권장 기본값”으로 박아놨고, 위험 지점은 체크리스트로 같이 달았어.)

A) 일반 사용자(4) 회원가입 → 사용 → 탈퇴 플로우 (1-2 중심)
flowchart LR
  %% Lanes
  subgraph OUR["1. OUR"]
    direction TB
    subgraph LICS["1-1 License Mgmt Server"]
      LIC1[License APIs\n(irrelevant for 일반 사용자)]
    end
    subgraph CONS["1-2 Consumer/User Server"]
      U1[Auth (Email/Passkey)\nAccount + Personal Profile]
      U2[Personal Workspace DB\n(User docs/ideas/settings)]
      U3[Privacy/Retention Policy Engine]
      U4[Export Service]
      U5[Deletion Service\n(soft->hard)]
      U6[Audit Log (User-plane)\n(optional)]
    end
  end

  subgraph GEN["4. 일반 사용자"]
    direction TB
    G1[Sign up]
    G2[Verify Email/Passkey]
    G3[Use Personal Workspace]
    G4[Request Export]
    G5[Delete Account]
    G6[Re-activate within grace?]
  end

  G1 --> U1 --> G2
  G2 --> U2 --> G3

  %% optional export
  G4 --> U4 --> G3

  %% delete flow
  G5 --> U5 --> U3
  U5 -->|Soft delete\n(grace window)| G6
  G6 -->|Yes| U1
  G6 -->|No| U5
  U5 -->|Hard delete\nafter N days| U2

일반 사용자 고려사항 체크리스트(초안)

계정/보안

 Email/Passkey 중 기본값 확정, MFA 옵션 여부

 로그인 세션/토큰 만료/기기 로그아웃(“Sign out all devices”)

 계정 도용 대비: 로그인 알림, 이상 징후 차단(기본만)

데이터

 Export 포맷(예: JSON + attachments zip)과 범위(문서/설정/로그)

 삭제 정책: Soft delete(유예) + Hard delete(영구삭제) 기간(N일)

 삭제 시 백업/스냅샷/캐시/검색인덱스/벡터 인덱스까지 포함해 “진짜 삭제” 정의

법/정책

 유료 플랜이 있다면 “결제 데이터” 보존 기간(회계) 분리

 CS/분쟁 대비 최소 로그(가입/탈퇴/결제)만 별도 보존할지

B) B2B 사용자(3) 가입 → 사내 서버 등록/승인 → 사용 → 퇴사(데이터 처리)

전제: 너가 말한 것처럼 공용 서버(1-2)에서 로그인/계정을 만들고, 회사 데이터는 B2B 고객 서버(2) 에 저장.

flowchart LR
  %% Lanes
  subgraph OUR["1. OUR"]
    direction TB
    subgraph LICS["1-1 License Mgmt Server"]
      L1[Tenant registry (minimal)\nlicense status, server registry]
    end
    subgraph CONS["1-2 Consumer/User Server"]
      C1[Global Account\n(Auth + Identity Link)]
      C2[Membership Store\n(account<->tenant, status)]
      C3[Role Binding\n(Tenant Admin/Member)]
      C4[Control-plane Audit Log\n(invite/approve/role change)]
      C5[Token Exchange\n(access for tenant server)]
    end
  end

  subgraph TEN["2. B2B 고객 서버 (Tenant On-prem)"]
    direction TB
    T1[Tenant Workspace API\n(Data-plane)]
    T2[Tenant Data Store\n(docs/ideas/index/embeddings)]
    T3[Tenant Data Audit Log\n(open/export/share)]
    T4[Lock Mode Controller\n(license expired)]
  end

  subgraph B2BU["3. B2B 사용자"]
    direction TB
    B1[Sign up / Login\n(central)]
    B2[Join Company\nvia Invite OR SSO]
    B3[Await Approval\n(if required)]
    B4[Use Tenant Workspace]
    B5[Resign / Termination]
  end

  %% entry
  B1 --> C1

  %% join paths
  B2 -->|Invite link| C2
  B2 -->|SSO login| C1
  C1 --> C2
  C2 -->|pending_approval| B3
  B3 -->|Admin approves| C3
  C3 -->|active| C2

  %% access tenant
  C2 -->|active| C5 --> T1 --> T2
  T1 --> T3
  B4 --> T1

  %% termination
  B5 --> C2 -->|terminated| C4
  C2 -->|revoke tokens| C5
  C5 -->|deny| T1

B2B 사용자 퇴사 시 “데이터 처리” 고려사항 체크리스트(초안)

여기서 사고 나는 지점만 콕 집어 체크리스트로 박아둘게.

접근 차단(즉시성)

 퇴사 이벤트 트리거: HR/IdP/SCIM/관리자 수동 중 최소 1개는 반드시

 Membership=terminated 즉시 토큰 revoke + 재발급 금지

 온프레미스도 동일하게 차단(세션 만료/토큰 거부)

데이터 소유권(가장 위험)

 “개인이 만든 문서”라도 회사 테넌트에 저장된 순간 소유권은 회사로 볼지

 퇴사 시 개인에게 “복사본 export” 허용/금지 정책(보통 금지 또는 제한)

 문서/오너십: Owner reassignment 규칙(상사/팀/관리자)

개인 프로필 vs 회사 프로필

 중앙(1-2) 계정은 그대로 유지(개인 사용 가능) vs 회사가 계정 폐쇄 요구 가능(정책)

 동일 이메일로 개인/회사 혼재 시 “회사 탈퇴 후 개인 데이터 접근” 경계 명확히

보존/감사

 퇴사자의 활동 로그 보존 기간(회사 정책 + 법규)

 Legal hold(삭제 금지) 옵션

C) B2B 고객 서버(2) 계약 → 설치/등록 → 사용 → 라이선스 만료/종료 시나리오

여기서 너가 원한 “계약부터 tenant server 인증 허가 등록 설치 사용 라이선스 만료 사용 종료”까지를 한 장에 넣었어.

flowchart LR
  %% Lanes
  subgraph OUR["1. OUR"]
    direction TB
    subgraph LICS["1-1 License Mgmt Server"]
      L0[Contract/Order\n(offline record)]
      L1[Issue Tenant ID + License\n(active, expiry, seats)]
      L2[Bootstrap Token\n(one-time, short TTL)]
      L3[Server Registry\n(cert fingerprint, status)]
      L4[License Check API\n(allow/deny)]
      L5[Grace/Retention Policy\n(control-plane metadata)]
      L6[Disable Tenant Access\n(revoke approvals)]
    end
    subgraph CONS["1-2 Consumer/User Server"]
      C1[Account/Membership\n(used by employees)]
      C2[Admin Console (control)\ninvite/approve/roles]
    end
  end

  subgraph TEN["2. B2B 고객 서버 (Tenant On-prem)"]
    direction TB
    S1[Install Tenant Server]
    S2[Generate Keypair/CSR]
    S3[Register to License Server\n(outbound HTTPS + mTLS)]
    S4[Receive Server Cert\n(pin fingerprint)]
    S5[Run Workspace\n(data-plane)]
    S6[Periodic Heartbeat\nlicense check]
    S7[LOCK MODE\n(license expired)]
    S8[Read-only/Export?\n(policy)]
    S9[Decommission\n(customer action)]
  end

  %% Contract -> onboarding
  L0 --> L1 --> L2
  S1 --> S2 -->|use bootstrap token| S3 --> L3
  L3 --> L4 --> S4
  S4 --> S5

  %% runtime checks
  S6 --> L4
  L4 -->|ALLOW| S5
  L4 -->|DENY: expired| S7 --> S8

  %% end of service
  L5 --> L6
  S8 -->|customer confirms end| S9

B2B 고객(테넌트) 라이선스 만료/종료 시 체크리스트(초안)

만료 시 동작 정의(“못 쓴다”의 의미)

 만료 즉시 차단 범위: 로그인/승인/권한변경/AI 실행/쓰기/검색 중 무엇을 막나

 만료 상태에서 허용: Read-only / Export / Admin-only export 중 선택

 Grace period: 0/30/90일 등 기본값 + 계약 옵션화

중앙 서버 데이터(컨트롤플레인 메타데이터)

 만료 후 중앙에 남는 것: tenant_id, membership 상태, 서버 등록/상태, 감사 로그 최소

 유예 종료 후 처리: 완전 삭제 vs 익명화 보존(청구/감사 최소)

 “테넌트 존재 노출” 방지(열거 공격) 정책

온프레미스 데이터(고객 소유)

 원칙: 삭제 강제 금지(분쟁 위험) / 고객이 decommission 선택

 고객이 원하면 “완전 삭제 버튼” 제공(키 폐기 포함)

 백업/스냅샷/인덱스/벡터까지 포함한 삭제 정의

Air-gapped 옵션(폐쇄망)

 오프라인 라이선스 번들(서명) 발급/갱신 절차

 서버 시간 조작 대응(탐지/운영 정책)

다음 작업 순서(너가 말한 “순차적으로 하나씩 정리” 그대로)

지금 초안이 “그림만 있는 상태”라면, 다음은 결정이 필요한 빈칸을 채워야 흐름도가 “최종”이 돼.

만료 시 Lock mode 정책: hard lock vs read-only + export (기본값 1개)

Grace period 기본값(예: 30일) + 옵션화 여부

퇴사 시 개인 export 허용 여부(대부분 금지/제한)

테넌트 합류 기본 정책: SSO만으로 auto-active 금지(=기본 pending_approval) 유지 여부

너가 위 4개 중에서 **1)~2)**만 먼저 찍어줘도, 내가 이 흐름도를 “정책이 박힌 버전(최종형)”으로 다듬어서 다음 턴에 바로 낼 수 있어.