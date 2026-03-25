from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools import get_stock_data, get_indicators
from .config import get_config

def create_market_analyst():
    config = get_config()
    
    # Initialize the LLM (API Key should be in .env)
    llm = ChatGoogleGenerativeAI(model=config["model_name"])
    
    tools = [get_stock_data, get_indicators]
    
    system_message = (
        """You are a financial market analyst assistant. Your goal is to provide a detailed, data-driven report of market condition using technical indicators.
Focus on these EXACT indicator names:
1.  **Trend**: 'close_50_sma', 'close_200_sma'
2.  **Momentum**: 'rsi'
3.  **Volatility**: 'boll', 'boll_ub', 'boll_lb'
4.  **MACD**: 'macd', 'macds', 'macdh'

Instructions:
1. Always start by fetching stock data with `get_stock_data`.
2. Based on the data, choose the most relevant indicators (max 5) and fetch them with `get_indicators`.
3. Provide a nuanced, fine-grained report including a final recommendation: **BUY/HOLD/SELL**."""
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"{system_message}\n\nCurrent date is {{current_date}}. Stock for analysis: {{ticker}}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Simplified chain: prompt -> bind tools -> llm
    chain = prompt | llm.bind_tools(tools)
    
    return chain

def run_analyst(chain, ticker, date):
    # Initial trigger message
    msg = f"Please provide a comprehensive market analysis report for {ticker} on {date}."
    
    # Simple loop to handle tool calls (manual orchestration for learning)
    messages = [("user", msg)]
    
    # Loop max 5 times for tool calling to avoid infinite loops
    for _ in range(10):
        result = chain.invoke({"messages": messages, "current_date": date, "ticker": ticker})
        messages.append(result)
        
        # If no more tool calls or AI provided a final answer, we're done
        if not hasattr(result, "tool_calls") or not result.tool_calls:
            return result.content
            
        # Execute tool calls
        for tool_call in result.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            
            # Map tool name to function
            tool_fn = {"get_stock_data": get_stock_data, "get_indicators": get_indicators}.get(name)
            
            if tool_fn:
                print(f"Executing tool {name} with args {args}...")
                tool_output = tool_fn.invoke(args)
                messages.append({
                    "role": "tool",
                    "content": str(tool_output),
                    "tool_call_id": tool_call["id"]
                })
    
    # Final fallback if it takes too many steps
    last_msg = messages[-1]
    return last_msg.content if hasattr(last_msg, "content") else "Analysis stopped after multiple tool calls."
