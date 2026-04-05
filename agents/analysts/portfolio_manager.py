from datetime import datetime
from typing import Dict, List, Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from agents.utils.agent_state import get_model_content_text

class PortfolioManager:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        
        self.system_prompt = (
            "You are a Senior Portfolio Manager and Investment Committee Head. "
            "Your role is to review detailed reports from your analysts and provide a final, "
            "authoritative investment decision.\n\n"
            "You will be provided with:\n"
            "1. A Market Analysis Report (Technical Analysis)\n"
            "2. A Fundamentals Analysis Report (Corporate Financials)\n\n"
            "Your output must follow this format:\n"
            "--- FINAL DECISION ---\n"
            "[DECISION]: (BUY, HOLD, or SELL)\n"
            "[CONFIDENCE]: (0-100%)\n"
            "[RATIONALE]: (A concise summary of why you reached this decision, balancing the technical and fundamental reports)\n"
            "--- END OF REPORT ---"
        )

    def analyze(self, state: Dict) -> Dict:
        """
        Final decision node. Does not take any tools.
        Expects market_report and fundamental_report to be present in the state.
        """
        ticker = state.get("ticker", "UNKNOWN")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))
        market_report = state.get("market_report", "No market analysis available.")
        fundamental_report = state.get("fundamental_report", "No fundamental analysis available.")

        print(f"\n[PortfolioManager] Making final decision for {ticker}...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", (
                f"Please review these reports for {ticker} as of {date} and provide a final decision.\n\n"
                f"### Market Analysis Report:\n{market_report}\n\n"
                f"### Fundamental Analysis Report:\n{fundamental_report}"
            )),
        ])
        
        chain = prompt | self.llm
        
        # Invoke LLM
        result = chain.invoke({})
        
        content = get_model_content_text(result.content)
        
        # Simple extraction of the decision from the text
        decision = "HOLD"
        content_upper = content.upper()
        if "[DECISION]: BUY" in content_upper:
            decision = "BUY"
        elif "[DECISION]: SELL" in content_upper:
            decision = "SELL"
        
        return {
            "final_decision": decision,
            "full_decision_report": content,
            "messages": [result]
        }

# Node instance
portfolio_manager_instance = PortfolioManager()

def portfolio_manager_node(state: Dict):
    return portfolio_manager_instance.analyze(state)
