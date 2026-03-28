import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# dataflows에서 데이터 관련 유틸리티 임포트
from dataflows.y_finance import (
    get_fundamentals, 
    get_balance_sheet, 
    get_income_statement, 
    get_cashflow, 
    get_insider_transactions
)

# --- Tools Definition ---

@tool
def get_company_overview(ticker: Annotated[str, "The stock ticker symbol"]):
    """Fetch company profile, sector, industry, and key valuation metrics (PE, PEG, etc.)."""
    return get_fundamentals(ticker)

@tool
def get_financial_statements(
    ticker: Annotated[str, "The stock ticker symbol"],
    statement_type: Annotated[str, "Statement: balance_sheet, income_statement, or cashflow"],
    frequency: Annotated[str, "Frequency: quarterly or annual"] = "quarterly"
):
    """Fetch financial statements for fundamental analysis."""
    if statement_type == "balance_sheet":
        return get_balance_sheet(ticker, frequency)
    elif statement_type == "income_statement":
        return get_income_statement(ticker, frequency)
    elif statement_type == "cashflow":
        return get_cashflow(ticker, frequency)
    else:
        return f"Unknown statement type: {statement_type}"

@tool
def get_insider_trading(ticker: Annotated[str, "The stock ticker symbol"]):
    """Fetch recent insider transactions for fundamental signals."""
    return get_insider_transactions(ticker)

# --- Analyst Logic ---

class FundamentalsAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.tools = [get_company_overview, get_financial_statements, get_insider_trading]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = (
            "You are a professional Fundamentals Analyst specializing in corporate financials and valuation. "
            "Your goal is to provide a detailed, data-driven assessment of a company's underlying health.\n"
            "Focus on these aspects:\n"
            "1. Valuation: PE Ratio, Forward PE, PEG Ratio, Price to Book.\n"
            "2. Financial Health: Balance Sheet (Net Debt/Equity), Income Statement (Profit Margins, Revenue Growth).\n"
            "3. Cash Flows: Operating and Free Cash Flow.\n"
            "4. Insider Confidence: Recent buy/sell signals from company insiders.\n\n"
            "Instructions:\n"
            "1. Fetch company overview and valuation metrics.\n"
            "2. Fetch financial statements and assess trends.\n"
            "3. Provide a final fundamental evaluation for the stock."
        )

    def analyze(self, state: Dict) -> Dict:
        """
        Fundamentals analyst node logic for LangGraph.
        Expects a state with 'messages', 'ticker', and 'date'.
        """
        messages = state.get("messages", [])
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))

        # 메시지가 비어있다면 에이전트에게 시작 신호를 줍니다.
        if not messages:
            messages = [HumanMessage(content=f"Please perform a fundamental analysis for {ticker} on {date}.")]

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + f"\nTarget: {ticker}, Date: {date}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm_with_tools
        
        # Invoke LLM
        result = chain.invoke({"messages": messages})
        
        return {"messages": [result]}

# Node instances for easier use in graph/setup.py
fundamentals_analyst_instance = FundamentalsAnalyst()

def fundamentals_analyst_node(state: Dict):
    return fundamentals_analyst_instance.analyze(state)
