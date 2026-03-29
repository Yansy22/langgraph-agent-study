import os
from datetime import datetime
from typing import Dict, List, Any

# graph/setup.py에서 컴파일된 그래프와 상태 정의 임포트
from graph.setup import graph as trading_graph

class TradingGraphFacade:
    """
    LangGraph 실행 전/후 처리를 담당하는 Facade 클래스.
    복잡한 노드 흐름을 숨기고 간단한 .execute() 인터페이스를 제공.
    """
    
    def __init__(self, ticker: str, date: str = None):
        self.ticker = ticker
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.graph = trading_graph

    def execute(self) -> Dict[str, Any]:
        """
        그래프 실행을 시작하고 최종 상태를 반환.
        """
        # Initial State
        initial_state = {
            "messages": [], # Initial trigger message
            "ticker": self.ticker,
            "date": self.date
        }
        
        # Add a trigger message to start the flow
        initial_state["messages"].append(
            ("user", f"Please perform a market analysis for {self.ticker} on {self.date}.")
        )
        
        # Run graph
        # StateGraph returns the final state after processing
        final_state = self.graph.invoke(initial_state)
        
        # Post-processing (Format report, extract final answer)
        return self._format_result(final_state)

    def _format_result(self, state: Dict) -> Dict:
        """
        최종 상태에서 필요한 정보만 추출하여 가공.
        """
        messages = state.get("messages", [])
        
        market_report = state.get("market_report", "No market report generated.")
        fundamental_report = state.get("fundamental_report", "No fundamental report generated.")
        
        full_report = (
            f"=== [Market Analysis Report] ===\n{market_report}\n\n"
            f"=== [Fundamental Analysis Report] ===\n{fundamental_report}"
        )
        
        return {
            "ticker": state.get("ticker"),
            "date": state.get("date"),
            "full_report": full_report,
            "messages_count": len(messages)
        }


# Simplified function-based facade
def run_trading_flow(ticker: str, date: str = None):
    facade = TradingGraphFacade(ticker, date)
    return facade.execute()

