import os
from datetime import datetime
from typing import Dict, List, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from agents.utils.agent_state import get_model_content_text
from agents.utils.pdf_generator import create_stock_pdf

class ReportAnalyst:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)
        
        self.system_prompt = (
            "You are a Professional Financial Report Editor. Your task is to take various analyst reports and synthesize them into a 'Pyramid Style' Executive Report.\n\n"
            "The report MUST follow this structure:\n"
            "1. EXECUTIVE SUMMARY (Top Priority): Ticker, Date, Decision, and 3 key bullet points summarizing the 'Why'.\n"
            "2. CAUSAL INSIGHTS: A brief explanation of what is driving the stock (Fundamental vs Macro vs Technical).\n"
            "3. RISK & OUTLOOK: Key risks to monitor.\n"
            "4. SUPPORTING DETAILS: Include the full text of previous reports under clear headers.\n\n"
            "Make it professional, concise, and easy to read for an executive."
        )

    def analyze(self, state: Dict) -> Dict:
        ticker = state.get("ticker", "UNKNOWN")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # Collect all reports
        market = state.get('market_report', 'N/A')
        fundamentals = state.get('fundamental_report', 'N/A')
        micro_news = state.get('micro_news_report', 'N/A')
        fundamental_news = state.get('fundamental_news_report', 'N/A')
        final_causal = state.get('full_decision_report', 'N/A')

        full_context = f"""
- Market Analysis: {market}
- Fundamentals Analysis: {fundamentals}
- Macro News Analysis: {micro_news}
- Company News Analysis: {fundamental_news}
- Final Causal Analysis & Decision: {final_causal}
"""

        print(f"\n[ReportAnalyst] Generating professional report for {ticker}...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"Please synthesize the final report for {ticker} on {date} based on these analysts' findings:\n{full_context}")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})

        final_markdown = get_model_content_text(result.content)
        
        # Generate PDF
        try:
            pdf_path = create_stock_pdf(final_markdown, ticker, date)
            print(f"[ReportAnalyst] PDF successfully generated: {pdf_path}")
        except Exception as e:
            print(f"[ReportAnalyst] Warning: Failed to generate PDF: {e}")
            pdf_path = None

        return {
            "full_decision_report": final_markdown, # Overwrite with the polished version
            "pdf_path": pdf_path
        }

# Node instance
report_analyst_instance = ReportAnalyst()

def report_analyst_node(state: Dict):
    return report_analyst_instance.analyze(state)
