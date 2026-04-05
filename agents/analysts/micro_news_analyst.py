import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from dataflows.y_finance import get_macro_news
from agents.utils.agent_state import get_model_content_text

# --- Tools Definition ---

@tool
def fetch_macro_news() -> str:
    """Fetch current market-wide (macro) economic news."""
    return get_macro_news()

# --- Analyst Logic ---

class MicroNewsAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.tools = [fetch_macro_news]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = (
            "You are a Macro Economic Analyst. Your job is to analyze market-wide news and determine the overall sentiment of the economy.\n"
            "Focus on:\n"
            "1. Interest rate trends (Fed decisions).\n"
            "2. Inflation (CPI, PCE).\n"
            "3. Global geopolitical events.\n"
            "4. Overall market sentiment (Bullish vs Bearish).\n\n"
            "Instructions:\n"
            "1. Fetch the macro news.\n"
            "2. Summarize the key economic drivers for the past month.\n"
            "3. Determine if the current macro environment is supportive or restrictive for the stock market."
        )

    def analyze(self, state: Dict) -> Dict:
        messages = state.get("messages", [])
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))

        new_messages = []
        if not messages:
            start_msg = HumanMessage(content=f"Please analyze the macro economic environment for {date}.")
            messages = [start_msg]
            new_messages.append(start_msg)

        print(f"\n[MicroNewsAnalyst] Date: {date}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + f"\nDate: {date}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm_with_tools
        result = chain.invoke({"messages": messages})

        new_messages.append(result)
        res = {"messages": new_messages}
        
        if not (hasattr(result, "tool_calls") and result.tool_calls):
            res["micro_news_report"] = get_model_content_text(result.content)
            
        return res

# Node instance
micro_news_analyst_instance = MicroNewsAnalyst()

def micro_news_analyst_node(state: Dict):
    return micro_news_analyst_instance.analyze(state)
