import yfinance as yf
import pandas as pd
from typing import Dict, Tuple

def check_stock_gatekeeper(ticker: str) -> Tuple[bool, str]:
    """
    주식 분석을 시작하기 전, 최소 조건을 만족하는지 검사하는 함수.
    LLM을 사용하지 않고 순수 파이썬 로직으로 실행됨.
    """
    try:
        t = yf.Ticker(ticker.upper())
        
        # 1. 최근 20일(약 1개월) 데이터 가져오기
        history = t.history(period="20d")
        
        if history.empty:
            return False, f"'{ticker}'에 대한 주가 데이터를 찾을 수 없습니다."

        # 2. 평균 거래량 체크 (사용자 기준: 50만 주)
        avg_volume = history['Volume'].mean()
        min_volume_threshold = 500000 
        
        if avg_volume < min_volume_threshold:
            return False, f"평균 거래량이 {avg_volume:,.0f}주로 기준치(500,000주)에 미달합니다."

        # 3. 시가총액 체크 (너무 작은 잡주 방지 - 예: 500억 이하)
        info = t.info
        market_cap = info.get('marketCap', 0)
        min_market_cap = 1_000_000_000 # 500억 (단위: 원/달러 기준에 따라 다름)
        
        # 참고: 미국 시장의 경우 보통 5천만 달러($50M) 이하를 초소형주로 봄
        if market_cap > 0 and market_cap < min_market_cap:
             return False, f"시가총액이 {market_cap:,.0f}로 너무 작아 위험성이 높습니다."

        return True, "분석 적합 종목입니다."

    except Exception as e:
        return False, f"게이트키퍼 검사 중 오류 발생: {str(e)}"

def gatekeeper_node(state: Dict) -> Dict:
    """
    Langgraph에서 사용할 게이트키퍼 노드
    """
    ticker = state.get("ticker", "UNKNOWN")
    print(f"\n[Gatekeeper] Checking criteria for {ticker}...")
    
    is_passed, reason = check_stock_gatekeeper(ticker)
    
    if is_passed:
        print(f"[Gatekeeper] ✅ PASS: {reason}")
        return {"gatekeeper_passed": True, "gatekeeper_reason": reason}
    else:
        print(f"[Gatekeeper] ❌ FAIL: {reason}")
        # 실패 시 로그를 남기고 종료로 유도하기 위한 상태 업데이트
        return {
            "gatekeeper_passed": False, 
            "gatekeeper_reason": reason,
            "full_decision_report": f"### 분석 중단 알림\n해당 종목({ticker})은 선정 기준에 미달하여 분석을 진행하지 않습니다.\n**사유:** {reason}"
        }
