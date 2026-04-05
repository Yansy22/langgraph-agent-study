import os
from datetime import datetime
from typing import Annotated, Dict, List, TypedDict, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from dataflows.y_finance import get_price_performance
from agents.utils.agent_state import get_model_content_text

# --- Tools Definition ---

@tool
def check_price_change(ticker: Annotated[str, "The stock ticker symbol"], date: Annotated[str, "current analysis date in YYYY-MM-DD"]) -> str:
    """Fetch the actual price performance compared with 1 week and 1 month ago."""
    return get_price_performance(ticker, date)

# --- Analyst Logic ---

class FinalAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        self.tools = [check_price_change]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = (
            "You are a Senior Strategic Analyst. Your ultimate goal is to provide a 'Causal Analysis' that explains the 'Why' behind recent stock price movements.\n\n"
            "MANDATORY FIRST STEP: You MUST call the 'check_price_change' tool to see how the price has actually performed over the last 1 week and 1 month.\n\n"
            "After receiving the price data, combine it with the provided Technical, Financial, and News reports to explain the price action.\n"
            "- If the price went DOWN: Is it because of macro factors, poor fundamentals, or technical overselling?\n"
            "- If the price went UP: Is it due to positive news, strong earnings, or a market-wide rally?\n\n"
            "Your final response MUST be a comprehensive report including:\n"
            "1. Price Performance Summary (based on tool output).\n"
            "2. Primary Drivers of Movement (Connecting news/fundamentals to price).\n"
            "3. Causal Explanation (The 'Why').\n"
            "4. Future Outlook (Buy/Hold/Sell recommendation based on all facts)."
        )

    def analyze(self, state: Dict) -> Dict:
        messages = state.get("messages", [])
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))

        # Retrieve previous reports
        reports = f"""
--- PREVIOUS ANALYSES CONTEXT ---
- Market Technical Report: {state.get('market_report', 'Not available')}
- Fundamental Financial Report: {state.get('fundamental_report', 'Not available')}
- Macro Economic (Micro News) Report: {state.get('micro_news_report', 'Not available')}
- Company News (Fundamental News) Report: {state.get('fundamental_news_report', 'Not available')}
---------------------------------
"""

        new_messages = []
        if not messages:
            start_msg = HumanMessage(content=f"Please provide the final causal analysis for {ticker}. Start by checking the actual price performance compared to 1 week and 1 month ago.")
            messages = [start_msg]
            new_messages.append(start_msg)

        print(f"\n[FinalAnalyst] Ticker: {ticker}, Date: {date}")

        # Inject reports into a system-level instruction update
        system_instruction = self.system_prompt + f"\nTicker: {ticker}\nDate: {date}\n\n{reports}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm_with_tools
        result = chain.invoke({"messages": messages})

        new_messages.append(result)
        res = {"messages": new_messages}
        
        if not (hasattr(result, "tool_calls") and result.tool_calls):
            final_report = get_model_content_text(result.content)
            res["full_decision_report"] = final_report
            # Provide a recommendation based on the combined analysis
            res["final_decision"] = "Completed Causal Analysis" 
            
        return res

# Node instance
final_analyst_instance = FinalAnalyst()

def final_analyst_node(state: Dict):
    return final_analyst_instance.analyze(state)
