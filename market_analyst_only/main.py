from .analyst import create_market_analyst, run_analyst
import os
from dotenv import load_dotenv 

# 환경 변수 로드 호출
load_dotenv()


def main():
    ticker = "NVDA"
    date = "2026-01-01"
    
    print(f"--- Starting Market Analyst for {ticker} on {date} ---")
    
    # Initialize the analyst
    analyst_chain = create_market_analyst()
    
    # Run the analyst (will trigger tool calls automatically)
    report = run_analyst(analyst_chain, ticker, date)
    
    print(f"\n--- Final Analysis Report for {ticker} ---\n")
    
    if isinstance(report, list):
        print(report[0]['text'])
    else:
        print(report)

if __name__ == "__main__":
    main()
