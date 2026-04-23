# 🚀 LangGraph AI Trading Analyst - Project Roadmap & TODO

현재 주식 분석 시스템의 핵심 파이프라인(Gatekeeper -> Analysts -> Synthesis -> PDF)은 구축 완료되었습니다. 
다음 단계는 시스템의 '지능', '전략적 깊이', 그리고 '운영 효율'을 높이는 고도화 작업입니다. 
본 문서는 현재 흩어져 있던 아이디어와 장기적인 아키텍처 고도화 비전을 체계적으로 통합 관리합니다.

---

## 📌 최우선 과제 (High Priority: Refactoring & Architecture Alignment)
- [ ] **에이전트 기본 클래스 상속 통합**: `market_analyst.py` 등 모든 에이전트 모듈이 공용 구조인 `BaseAnalyst`(`agents/base.py`)를 상속하도록 리팩토링.
- [ ] **전역 헌법 및 부칙 적용**: `agents/rules/constitution.py`와 `bylaws.py`의 내용이 모든 에이전트의 시스템 프롬프트 최상단에 자동 주입되도록 파이프라인 연결.
- [ ] **Portfolio Manager 노드 편입**: `Final Analyst` 로직에서 자산 배분/최종 결정을 분리, `portfolio_manager.py` 노드를 메인 그래프(`setup.py`)에 정식 편입.
- [ ] **Pydantic Structured Output 파싱**: 결정 노드(BUY/HOLD/SELL)가 더 안정적으로 응답을 파싱할 수 있게 구조화된 데이터(Structured Output) 추출 로직 도입.

---

## 📅 단계별 고도화 로드맵 (Evolution Roadmap)

### Phase 1: 아키텍처 및 지능 모델 강화 (Graph Evolution & Intelligence)
- [ ] **병렬 실행 (Parallel Fan-out/Fan-in)**: Market, Fundamentals, News 분석 노드를 동시에 실행하여 전체 분석 시간 60~70% 단축.
- [ ] **멀티 에이전트 토론 (Debate)**: 강세론자(Bull)와 약세론자(Bear) 에이전트 도입 및 상호 토론 결과를 바탕으로 Final Analyst 판결 도출 (할루시네이션 방지).
- [ ] **자기 비판 및 가드레일 (Self-Correction & Safeguards)**: 최종 리포트에 논리적 허점이나 터무니없는 추천(예: 손절 구간 없는 매수)을 방지하는 '비판자(Red Team)' 및 수치 검증 노드 추가.
- [ ] **서브그래프(Subgraphs) 개편**: 특정 분석가의 역할을 독립된 서브그래프로 분리 (예: 거시경제 애널리스트 내부에 '금리/환율' 전문 Sub-Node를 둠).
- [ ] **확신 점수 (Confidence Score) 시스템**: 분석가들이 각자의 의견 제시 시 0~1.0 사이의 '확신도'를 동시에 출력, 최종 판단 노드에서 이 가중치를 참조하도록 로직 설계.
- [ ] **투자 페르소나 반영 (Persona)**: 공격형/배당형 등 사용자 성향을 Constitution에 삽입하여 동일 종목이라도 조건에 따른 맞춤 처방 도출.

### Phase 2: 최적화 및 전략 백테스트 (Performance & Strategy)
- [ ] **Multi-LLM 하이브리드 설계**: 
  - 단순 요약/텍스트 기반 파싱: `Gemini 1.5 Flash` (속도/비용 최적화)
  - 복잡한 연산, 최종 추론 및 의사결정: `Pro` 모델 계열 사용
- [ ] **멀티 레이어 캐싱 (Advanced Caching)**: 동일 종목 당일 1차 캐싱 외에 '유사한 시장 환경에서의 과거 패턴'까지 캐싱하여 처리 효율 향상.
- [ ] **시계열 지속성 메모리 (Checkpointers)**: 이전 시점 분석 결론 기억 (예: "지난번엔 매수 추천했으나, 이번 분기 결과가 기대에 미치지 못해 관망세로 전환한다" 같은 문맥 형성).
- [ ] **백테스팅(Backtesting) 엔진 연동**: 과거 차트 시뮬레이터(Backtrader 등) 연결, 해당 에이전트 전략의 승률과 누적 수익률을 리포트에 명시.
- [ ] **경량 금융 특화 NLP 분리**: 뉴스 문맥 분석 시汎용 LLM 대신 로컬 환경에서 가동 가능한 소형 감성 모델(FinBERT 등)을 활용해 정량 점수 지표로 도출 비용 절감.

### Phase 3: 데이터 영역 확장 (Deep Data Integration)
- [ ] **비정형 RAG 검색 연결**: API 기반 실시간 데이터(yfinance) 외에 기업 분기 보고서(10-K), 컨퍼런스 콜 스크립트를 Vector DB로 묶어 RAG 검색망 구축.
- [ ] **지식그래프 융합 (GraphRAG)**: 단순 키워드 검색을 초월한 맥락 파악. 
  - 특정 종목(NVDA) 분석 시 관련 고객사, 경쟁사 데이터까지 자동으로 스캔하는 **Supply Chain Analytics** 노드 신설.
- [ ] **Vision Agent (차트 인식)**: LLM의 Vision 기능을 적용해 RSI, 이동평균선 등의 주가 차트 이미지를 시각적으로 직접 독해하는 노드 설계.

### Phase 4: 인프라, 모니터링, 경험 (Infra & Observability)
- [ ] **실시간 분석 대시보드 (Web UI)**: Streamlit 혹은 Next.js를 활용하여, 에이전트들의 사고 체인(CoT) 전개 과정을 브라우저 단에서 실시간 확인 가능한 인터페이스 배포.
- [ ] **자동화 스케줄&알람 (Scheduler/CI)**: 장 시작 전/장 마감 직후 타겟 관심 종목 배치 분석 및 자동 텔레그램/슬랙 요약 알림망.
- [ ] **인적 피드백 시스템 (Human-In-The-Loop)**: 시스템 판단에 대한 인간 관리자의 교정 피드백 -> 로컬 `feedback.json` 누적 -> 다음 쿼리에 가중 반영.
- [ ] **토큰 관리 및 품질 측정 (DevOps & Eval)**:
  - Token Economy Dashboard: 노드/에이전트별 토큰 사용량 실시간 모니터링.
  - 프롬프트 버저닝 (Semantic Versioning): LangSmith 기반 A/B 테스트 성과 추적.
  - Test Automation: 애널리스트 단위 격리 테스트(Unit Test) 작성으로 회귀 사이클 차단.

---

## ✅ 완료 이력 (Completed Milestones)

- [x] **Python 기반의 Gatekeeper (사전 필터링)**: LLM 콜 전, 거래량 50만 및 시가총액 기반 허들을 설정하여 방어적인 실행 파이프라인 적용.
- [x] **Centralized Rules 구조화**: 전역 헌법(Constitution) 및 부칙(Bylaws)을 체계적으로 담기 위한 `agents/rules` 아키텍처 초안 설계 완료.
- [x] **Graph Routing & Edge 복구**: 중간에 발생하는 `__end__` 예약어 등 그래프 충돌 관련 로직 안정화. PDF Report 연결 복구.
- [x] **Multi-Agent 순차 연동**: 마켓 -> 펀더멘털 -> 거시경제 마이크로 -> 기업 분석 순으로 데이터를 바통 터치하는 파이프라인 개발 완료.
- [x] **PDF Generator**: 도출된 분석 결과를 텍스트에 한정 짓지 않고 시각적 리포트(PDF) 형태로 저장하는 후속 로직 장착.