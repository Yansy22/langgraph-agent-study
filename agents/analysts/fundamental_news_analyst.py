import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from dataflows.y_finance import get_stock_news
from agents.utils.agent_state import get_model_content_text

# --- Tools Definition ---

@tool
def fetch_stock_news(ticker: Annotated[str, "The stock ticker symbol"]) -> str:
    """Fetch company-specific news for fundamental analysis."""
    return get_stock_news(ticker)

# --- Analyst Logic ---

class FundamentalNewsAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.tools = [fetch_stock_news]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = (
            "You are a fundamental news analyst for specific companies. Your goal is to analyze company-specific events and evaluate their impact on the stock price.\n"
            "Analyze these factors:\n"
            "1. Earnings surprises or warnings.\n"
            "2. Strategic partnerships or product launches.\n"
            "3. Legal or regulatory developments.\n"
            "4. Management changes or insider behavior reported in news.\n\n"
            "Instructions:\n"
            "1. Fetch the latest news for the given ticker.\n"
            "2. Identify the most critical news items from the last month.\n"
            "3. Determine if the news environment for the company is positive, negative, or neutral."
        )

    def analyze(self, state: Dict) -> Dict:
        messages = state.get("messages", [])
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))

        new_messages = []
        if not messages:
            start_msg = HumanMessage(content=f"Please analyze the company news for {ticker} as of {date}.")
            messages = [start_msg]
            new_messages.append(start_msg)

        print(f"\n[FundamentalNewsAnalyst] Ticker: {ticker}, Date: {date}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + f"\nTicker: {ticker}\nDate: {date}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm_with_tools
        result = chain.invoke({"messages": messages})

        new_messages.append(result)
        res = {"messages": new_messages}
        
        if not (hasattr(result, "tool_calls") and result.tool_calls):
            res["fundamental_news_report"] = get_model_content_text(result.content)
            
        return res

# Node instance
fundamental_news_analyst_instance = FundamentalNewsAnalyst()

def fundamental_news_analyst_node(state: Dict):
    return fundamental_news_analyst_instance.analyze(state)
