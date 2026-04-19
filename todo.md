# 🚀 Project Roadmap & TODO

현재 주식 분석 시스템의 핵심 파이프라인(Gatekeeper -> Analysts -> Synthesis -> PDF)은 구축 완료되었습니다. 다음 단계는 시스템의 '지능', '전략적 깊이', 그리고 '운영 효율'을 높이는 고도화 작업입니다.

---

### 1. 지능 및 규칙 (Intelligence & Rules) 🧠
- [ ] **전역 헌법(Constitution) 주입**: `agents/rules/constitution.py`의 내용을 모든 에이전트의 시스템 프롬프트 최상단에 자동으로 삽입하는 로직 구현.
- [ ] **도메인 부칙(Bylaws) 연동**: 각 분석가(Macro, Fundamentals, Market)의 프롬프트에 `agents/rules/bylaws.py`의 전문 지식을 동적으로 임포트.
- [ ] **투자 페르소나 설정**: 사용자 성향(공격형/방어형)에 따른 분석 결론 도출 기능 추가.
- [ ] **멀티 에이전트 토론(Debate) 도입**: 강세론자/약세론자 에이전트 간의 토론 노드를 통해 할루시네이션 억제 및 비판적 분석 강화.
- [ ] **Gatekeeper 고도화**:
    - [x] (완료) Python 기반 하드 필터링 (Volume, Market Cap).
    - [ ] (예정) `bylaws.py`로 기준치 관리 이관 및 LLM 기반 소프트 필터링(Soft Rule) 노드 추가.

### 2. 워크플로우 및 전략 (Workflow & Strategy) 📈
- [ ] **Portfolio Manager 노드 통합**: `Final Analyst`(인과 분석)와 `Portfolio Manager`(자산 배분 및 최종 결정) 역할을 분리하여 그래프에 추가.
- [ ] **백테스팅(Backtesting) 연동**: 에이전트의 매수/매도 추천에 대한 과거 데이터 기반 수익률 검증 노드 추가.
- [ ] **메시지 리스트 세분화**: `AgentState` 내에서 '분석 데이터'와 '에이전트 간 대화 로그'를 분리하여 토큰 최적화.
- [ ] **실패 경로 복구(Retry Logic)**: 데이터 API 호출 실패 시 재시도하거나 대안 데이터를 찾는 에러 핸들링 강화.

### 3. 데이터 및 성능 최적화 (Data & Optimization) ⚡
- [ ] **Multi-LLM 하이브리드 전략**:
    - 단순 요약/검사: Gemini 1.5 Flash 사용
    - 심층 분석/의사결정: Pro 모델 사용
- [ ] **캐시 레이어 고도화**: 동일 종목의 당일 분석 요청 시 외부 API 호출 없이 저장된 캐시 데이터 활용 강화.
- [ ] **RAG(Retrieval-Augmented Generation) 통합**: 기업 공시(10-K), 컨퍼런스 콜 스크립트 등 비정형 데이터 검색 기능 추가.
- [ ] **경량 감성 분석 모델 분리**: 뉴스 분석 시 금융 특화 소형 모델(FinBERT 등)을 활용한 정량적 점수 산출.

### 4. 인프라 및 사용자 경험 (Infra & UX) 🖥️
- [ ] **실시간 분석 대시보드**: 에이전트의 사고 과정(Chain of Thought)을 실시간으로 시각화하는 웹 인터페이스(Streamlit/Next.js) 구축.
- [ ] **자동화 스케줄러 및 알림**: 장 시작/마감 전 자동 분석 실행 및 텔레그램/슬랙 알림 연동.
- [ ] **인적 피드백 루프(Human-in-the-loop)**: 에이전트의 판단에 대해 사용자가 피드백을 주고, 이를 다음 분석에 반영하는 학습 구조.

---

### 완료된 항목 (Ref. 2026-04-16) ✅
- [x] **Python Gatekeeper**: 거래량 50만 이하 종목 사전 필터링 (LLM 없이 구현).
- [x] **Centralized Rules**: 헌법 및 부칙 관리를 위한 `agents/rules` 구조 설계.
- [x] **Graph Routing Fix**: `__end__` 예약어 충돌 해결 및 PDF 리포트 생성 보장.
- [x] **Multi-Agent Flow**: 시장/재무/뉴스 분석가들의 순차적 분석 파이프라인 연동.
- [x] **PDF 생성**: 분석 결과를 시각화된 리포트로 자동 변환.


1. 기술적 고도화 (Technical Evolution)
RAG (Retrieval-Augmented Generation) 통합:
현재는 실시간 API(yfinance)에 의존하지만, 기업의 분기 보고서(10-K, 10-Q), 컨퍼런스 콜 스크립트 등을 **Vector DB(ChromaDB, Pinecone 등)**에 저장하고 분석가가 필요할 때마다 검색해서 참조하게 할 수 있습니다.
신뢰성 있는 가드레일 (Safe Guards):
LLM의 추천이 터무니없는 경우(예: 손절매 라인 없는 매수 추천)를 방지하기 위해 PydanticOutputParser를 사용하여 응답 형식을 강제하고, 수치적 검증 노드를 추가해야 합니다.
멀티 레이어 캐싱 (Advanced Caching):
동일 종목 데이터뿐만 아니라, 유사한 시장 환경에서의 과거 분석 패턴을 캐싱하여 재사용함으로써 비용을 획기적으로 낮출 수 있습니다.
2. 투자 전략의 정교화 (Investment Strategy)
백테스팅(Backtesting) 엔진 연동:
시스템이 내린 'BUY' 결정이 실제 과거 데이터에서 수익을 냈을지 검증하는 노드를 추가하세요. Backtrader나 VectorBT 같은 라이브러리와 연동하여 "이 에이전트의 승률은 65%입니다"라는 통계를 리포트에 포함할 수 있습니다.
멀티 에이전트 토론 (Multi-Agent Debate):
현재는 순차적 분석이지만, '강세론자(Bull) 에이전트'와 '약세론자(Bear) 에이전트'가 서로 토론하게 하고 Final Analyst가 판결을 내리는 구조로 바꾸면 할루시네이션이 줄어들고 비판적 사고가 강화됩니다.
포트폴리오 리밸런싱 로직:
개별 종목 분석을 넘어, 현재 보유한 전체 자산의 비중을 고려하여 "NVDA는 좋지만 이미 비중이 높으니 이번엔 건너뛰세요"와 같은 자산 배분(Asset Allocation) 관점의 조언 노드를 추가할 수 있습니다.
3. 운영 및 인프라 (Ops & Infrastructure)
실시간 대시보드 (Streamlit/Next.js):
PDF 리포트 생성에서 한 걸음 더 나아가, 에이전트들의 사고 과정(생각 체인)을 웹에서 실시간으로 볼 수 있는 대시보드를 구축하세요.
자동화 스케줄러 (GitHub Actions / Airflow):
매일 장 마감 후 또는 장 시작 전 자동으로 관심 종목 리스트를 스캔하고 텔레그램/슬랙으로 요약 보고서를 발송하는 기능을 추가할 수 있습니다.
인적 피드백 루프 (Human-in-the-loop):
에이전트의 결정에 사용자가 "이 분석은 틀렸어"라고 피드백을 주면, 그 내용이 data_cache/feedback.json에 저장되어 다음 분석 시 반영되는 학습 구조를 만들 수 있습니다.
4. 사용자 맞춤형 지능 (Personalization)
투자 페르소나 설정:
"나는 공격적인 성장주 투자자야" 또는 "나는 은퇴 자금을 위한 배당주 투자자야"라는 설정을 Constitution에 반영하여, 동일한 종목이라도 사용자 성향에 따라 다른 결론을 내리게 할 수 있습니다.
뉴스 감성 분석(Sentiment Analysis) 모델 분리:
뉴스 분석 시 범용 LLM 대신 금융 전용 작은 모델(FinBERT 등)을 로컬에서 실행하여 뉴스 톤을 수치화하고, 이를 LLM에 정량적 데이터로 넘겨줌으로써 정확도와 비용을 동시에 잡을 수 있습니다.