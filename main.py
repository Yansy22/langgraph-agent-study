import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 1. 환경 변수 로드부터 먼저 실행해야 함. .env 파일의 환경 변수 로드
load_dotenv()

# 2. [Layer 1] graph/trading_graph.py 로부터 파사드 임포트
from graph.trading_graph import run_trading_flow



def main():
    """
    애플리케이션 실행의 메인 진입점.
    사용자 입력을 받아 그래프 레이어를 호출합니다.
    """
    parser = argparse.ArgumentParser(description="AI Trading Analysis Tool")
    parser.add_argument("--ticker", type=str, default="NVDA", help="Trading ticker symbol (e.g., NVDA, AAPL)")
    parser.add_argument("--date", type=str, help="Analysis date in YYYY-MM-DD format (default: today)")
    
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    date = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
    
    print(f"🚀 AI Trading Analyst Starting [Ticker: {ticker}, Date: {date}]...")
    
    try:
        # [Facade] 실행 진입: 그래프 레이어의 trading_graph.py 호출
        result = run_trading_flow(ticker, date)
        
        print("\n" + "="*50)
        print(f"📅 [{result['date']}] {result['ticker']} 분석 결과")
        print(f"📢 최종 결정: {result['final_decision']}")
        print("="*50)
        print("\n" + result["full_report"])
        print("\n" + "="*50)
        print("Done.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
