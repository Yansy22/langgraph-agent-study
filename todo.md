# 🚀 Project Roadmap & TODO

현재 주식 분석 시스템의 핵심 파이프라인(Gatekeeper -> Analysts -> Synthesis -> PDF)은 구축 완료되었습니다. 다음 단계는 시스템의 '지능'과 '운영 효율'을 높이는 고도화 작업입니다.

---

### 1. 규칙 시스템 (Rules & Alignment) 적용 🛠️
- [ ] **전역 헌법(Constitution) 주입**: `agents/rules/constitution.py`의 내용을 모든 에이전트의 시스템 프롬프트 최상단에 자동으로 삽입하는 로직 구현.
- [ ] **도메인 부칙(Bylaws) 연동**: 각 분석가(Macro, Fundamentals, Market)의 프롬프트에 `agents/rules/bylaws.py`의 전문 지식을 동적으로 임포트.
- [ ] **Gatekeeper 고도화 (계획)**:
    - [x] (완료) Python 기반 하드 필터링 (Volume, Market Cap).
    - [ ] (예정) `bylaws.py`로 기준치 관리 이관 및 LLM 기반 소프트 필터링(Soft Rule) 노드를 하드 필터링 직후에 추가.

### 2. 워크플로우 정교화 (Graph Refinement) 🔄
- [ ] **Portfolio Manager 노드 통합**: `Final Analyst`(인과 분석)와 `Portfolio Manager`(최종 의사결정) 역할을 분리하여 그래프에 추가.
- [ ] **메시지 리스트 세분화**: `AgentState` 내에서 '분석 데이터'와 '에이전트 간 대화 로그'를 분리하여 토큰 낭비 방지 및 Context 윈도우 최적화.
- [ ] **실패 경로 복구(Retry Logic)**: 데이터 API 호출 실패 시 재시도하거나, 대안 데이터를 찾는 에러 핸들링 강화.

### 3. 성능 및 비용 최적화 (Optimization) 💰
- [ ] **Multi-LLM 하이브리드 전략**: 
    - 단순 요약/검사: Gemini 1.5 Flash 사용
    - 심층 분석/의사결정: Pro 모델 사용
- [ ] **캐시 레이어 고도화**: 동일 종목의 당일 분석 요청 시 외부 API 호출 없이 저장된 캐시 데이터 활용 강화.

---

### 완료된 항목 (Ref. 2026-04-16) ✅
- [x] **Python Gatekeeper**: 거래량 50만 이하 종목 사전 필터링 (LLM 없이 구현).
- [x] **Centralized Rules**: 헌법 및 부칙 관리를 위한 `agents/rules` 구조 설계.
- [x] **Graph Routing Fix**: `__end__` 예약어 충돌 해결 및 PDF 리포트 생성 보장.
- [x] **Multi-Agent Flow**: 시장/재무/뉴스 분석가들의 순차적 분석 파이프라인 연동.
- [x] **PDF 생성**: 분석 결과를 시각화된 리포트로 자동 변환.