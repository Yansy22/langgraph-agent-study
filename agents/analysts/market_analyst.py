import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# dataflows에서 데이터 관련 유틸리티 임포트
from dataflows.y_finance import get_YFin_data_online, get_stock_stats_indicators_window
from dataflows.stockstats_utils import StockstatsUtils 

# --- Tools Definition ---

@tool
def get_stock_prices(
    ticker: Annotated[str, "The stock ticker symbol"],
    start_date: Annotated[str, "Start date in YYYY-MM-DD format"],
    end_date: Annotated[str, "End date in YYYY-MM-DD format"]
) -> str:
    """Fetch historical stock price data for technical analysis."""
    return get_YFin_data_online(ticker, start_date, end_date)

@tool
def get_technical_indicators(
    ticker: Annotated[str, "The stock ticker symbol"],
    indicator: Annotated[str, "Indicator name: close_50_sma, close_200_sma, rsi, boll, macd"],
    current_date: Annotated[str, "The date for analysis in YYYY-MM-DD format"],
    look_back_days: Annotated[int, "Number of days to look back (default 30)"] = 30
) -> str:
    """Get technical indicator values for a given period."""
    return get_stock_stats_indicators_window(ticker, indicator, current_date, look_back_days)

# --- Analyst Logic ---

class MarketAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.tools = [get_stock_prices, get_technical_indicators]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = (
            "You are a professional Market Analyst specializing in technical analysis. "
            "Your goal is to provide a detailed, data-driven report of market conditions using technical indicators.\n"
            "Focus on these indicator categories:\n"
            "1. Trend: 50 SMA, 200 SMA\n"
            "2. Momentum: RSI\n"
            "3. Volatility: Bollinger Bands\n"
            "4. MACD\n\n"
            "Instructions:\n"
            "1. Start by fetching stock price data.\n"
            "2. Fetch relevant technical indicators.\n"
            "3. Provide a final recommendation: BUY, HOLD, or SELL with clear reasoning."
        )

    def analyze(self, state: Dict) -> Dict:
        """
        Market analyst node logic for LangGraph.
        Expects a state with 'messages', 'ticker', and 'date'.
        """
        messages = state.get("messages", [])
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))

        # 메시지가 비어있다면 에이전트에게 시작 신호를 줍니다.
        if not messages:
            messages = [HumanMessage(content=f"Please perform a market analysis for {ticker} on {date}.")]

        print(f"\n[MarketAnalyst] Target: {ticker}, Date: {date}")
        print(f"[MarketAnalyst] Message History Count: {len(messages)}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + f"\nTarget: {ticker}, Date: {date}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm_with_tools
        
        # Invoke LLM
        print("[MarketAnalyst] Calling LLM...")
        result = chain.invoke({"messages": messages})
        
        # 기본 반환값
        res = {"messages": [result]}
        
        # 만약 도구 호출이 없다면(최종 보고서라면), market_report에도 저장
        if not (hasattr(result, "tool_calls") and result.tool_calls):
            print("[MarketAnalyst] Final report generated.")
            res["market_report"] = result.content
        else:
            print(f"[MarketAnalyst] Tool calls detected: {[tc['name'] for tc in result.tool_calls]}")
            
        return res

# Node instances for easier use in graph/setup.py
market_analyst_instance = MarketAnalyst()

def market_analyst_node(state: Dict):
    return market_analyst_instance.analyze(state)
