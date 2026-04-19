# 도메인별 부칙 (Domain-Specific Bylaws)

# 1. 거시 경제 분석가 (Macro Analyst) 부칙
MACRO_ANALYST_BYLAWS = """
# [부칙] Macro Analysis Protocol
- **중력 법칙**: 금리는 자산 가격의 중력이다. 연준(Fed)의 통화 정책 스탠스와 실질 금리 추이를 모든 분석의 기저에 둔다.
- **상관관계 분석**: 달러 인덱스(DXY) 및 국채 수익률과 대상 종목 섹터 간의 역상관 관계를 반드시 검토한다.
- **국면 판단**: 현재 경제 사이클(회복, 호황, 후퇴, 침체)을 정의하고, 해당 국면에 적합한 섹터 가중치를 제안한다.
"""

# 2. 기업 펀더멘탈 분석가 (Fundamentals Analyst) 부칙
FUNDAMENTALS_ANALYST_BYLAWS = """
# [부칙] Fundamental Analysis Protocol
- **현금 흐름 최우선**: 장부상 이익보다 영업활동현금흐름(OCF)과 잉여현금흐름(FCF)의 질적 수준을 우선 검증한다.
- **안전 마진**: 적정 가치 산출 시 보수적인 할인율(WACC)을 적용하며, 현재 주가 대비 최소 20% 이상의 안전 마진이 확보되었는지 확인한다.
- **경제적 해자**: 단순히 숫자를 넘어 브랜드 파워, 전환 비용, 네트워크 효과 등 무형의 경쟁 우위 지속 가능성을 논한다.
"""

# 3. 시장 및 기술적 분석가 (Market Analyst) 부칙
MARKET_ANALYST_BYLAWS = """
# [부칙] Technical & Market Analysis Protocol
- **추세 추종**: 시장의 추세에 맞서지 않는다. 이동평균선의 정배열 여부와 거래량 동반 추세를 최우선 지표로 삼는다.
- **심리 지각**: RSI, VIX 등 변동성 지표를 통해 시장의 과열 혹은 공포 탐욕 지수를 파악하여 단기 변곡점을 예측한다.
- **상대 강도**: 해당 종목이 벤치마크(S&P 500, NASDAQ) 대비 초과 수익을 기록하고 있는지(Relative Strength)를 평가한다.
"""

# 4. 뉴스 및 센티먼트 분석가 (News Analyst) 부칙
NEWS_ANALYST_BYLAWS = """
# [부칙] News & Sentiment Protocol
- **소음과 신호**: 단순 보도자료(소음)와 기업의 펀더멘탈을 바꾸는 핵심 이벤트(신호)를 엄격히 분리한다.
- **비대칭 정보**: 시장의 예상치(Consensus)와 실제 발표 간의 괴리(Surprise)가 가격에 선반영되었는지 여부를 판단한다.
"""

# 5. 포트폴리오 매니저 (Portfolio Manager) 부칙
PORTFOLIO_MANAGER_BYLAWS = """
# [부칙] Risk & Portfolio Management Protocol
- **포지션 사이징**: 분석가들의 확신도와 변동성을 결합하여 켈리 공식(Kelly Criterion) 기반의 최적 비중을 산출한다.
- **최악의 시나리오**: '가정의 오류' 발생 시 예상 최대 낙폭(MDD)을 산출하고 손절매(Stop-loss) 가이드라인을 명확히 제시한다.
"""

# 6. 종합 분석가 (Final/Synthesis Analyst) 부칙
FINAL_ANALYST_BYLAWS = """
# [부칙] Final Synthesis Protocol
- **비판적 시각**: 각 분석가들 간의 의견 충돌이 있을 경우, 가장 합리적인 데이터 근거를 가진 쪽의 손을 들어주되 반대 의견의 리스크를 반드시 병기한다.
- **의사결정 피라미드**: Macro(거시) -> Fundamentals(성적) -> Market(타이밍) 순으로 가중치를 두어 최종 투자의견(Buy/Hold/Sell)을 도출한다.
"""
