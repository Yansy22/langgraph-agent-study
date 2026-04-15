from typing import Annotated, Dict, List, Literal, TypedDict, Union
import operator

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Analyst 노드 및 데이터 레이어 임포트
from agents.analysts.market_analyst import market_analyst_node, market_analyst_instance
from agents.analysts.fundamentals_analyst import fundamentals_analyst_node, fundamentals_analyst_instance
from agents.analysts.micro_news_analyst import micro_news_analyst_node, micro_news_analyst_instance
from agents.analysts.fundamental_news_analyst import fundamental_news_analyst_node, fundamental_news_analyst_instance
from agents.analysts.final_analyst import final_analyst_node, final_analyst_instance
from agents.analysts.report_analyst import report_analyst_node
from agents.analysts.portfolio_manager import portfolio_manager_node, portfolio_manager_instance
from agents.utils.agent_state import AgentState

# --- Graph Logic ---

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """도구 호출 여부에 따라 다음 경로 결정"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 마지막 메시지에 tool_calls가 있으면 해당 도구 노드로 이동
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"  [Router] Tools detected, routing to next tool node.")
        return "tools"
    
    # 도구 호출이 없으면 현재 분석 단계를 종료하고 다음 분석가로 이동
    print(f"  [Router] No tools detected, finishing current analysis segment.")
    return "__end__"

# 전용 도구 노드 분리
# 1. 시장 분석가 전용 도구 노드
market_tools = ToolNode(market_analyst_instance.tools)
# 2. 기본적 분석가 전용 도구 노드
fundamentals_tools = ToolNode(fundamentals_analyst_instance.tools)
# 3. 거시 경제 뉴스 전용 도구 노드
micro_news_tools = ToolNode(micro_news_analyst_instance.tools)
# 4. 기업 뉴스 전용 도구 노드
fundamental_news_tools = ToolNode(fundamental_news_analyst_instance.tools)
# 5. 최종 분석가 전용 도구 노드
final_tools = ToolNode(final_analyst_instance.tools)

# --- Graph Assembly ---

# 1. 메시지 삭제 노드 정의
def clear_messages_node(state: AgentState):
    print("\n[System] Clearing messages for the next agent segment...")
    return {"messages": "CLEAR"}


def create_trading_graph():
    workflow = StateGraph(AgentState)

    # 1. 모든 노드 추가 (노드 추가가 엣지 설정보다 앞에 와야 함)
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("market_tools", market_tools)
    workflow.add_node("clear_market_messages", clear_messages_node)
    
    workflow.add_node("fundamentals_analyst", fundamentals_analyst_node)
    workflow.add_node("fundamentals_tools", fundamentals_tools)
    workflow.add_node("clear_fundamentals_messages", clear_messages_node)

    workflow.add_node("micro_news_analyst", micro_news_analyst_node)
    workflow.add_node("micro_news_tools", micro_news_tools)
    workflow.add_node("clear_micro_news_messages", clear_messages_node)

    workflow.add_node("fundamental_news_analyst", fundamental_news_analyst_node)
    workflow.add_node("fundamental_news_tools", fundamental_news_tools)
    workflow.add_node("clear_fundamental_news_messages", clear_messages_node)

    workflow.add_node("final_analyst", final_analyst_node)
    workflow.add_node("final_tools", final_tools)
    
    workflow.add_node("report_analyst", report_analyst_node)
    
    # 2. 진입점 설정
    workflow.set_entry_point("market_analyst")
    
    # 3. 엣지 및 조건부 로직 설정
    # ---------------------------------------------------------
    # 시장 분석가(Market Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "market_analyst",
        should_continue,
        {
            "tools": "market_tools",
            "__end__": "clear_market_messages"
        }
    )
    workflow.add_edge("market_tools", "market_analyst")
    workflow.add_edge("clear_market_messages", "fundamentals_analyst")
    
    # ---------------------------------------------------------
    # 기본적 분석가(Fundamentals Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "fundamentals_analyst",
        should_continue,
        {
            "tools": "fundamentals_tools",
            "__end__": "clear_fundamentals_messages"
        }
    )
    workflow.add_edge("fundamentals_tools", "fundamentals_analyst")
    workflow.add_edge("clear_fundamentals_messages", "micro_news_analyst")

    # ---------------------------------------------------------
    # 거시 경제 뉴스 분석가(Micro News Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "micro_news_analyst",
        should_continue,
        {
            "tools": "micro_news_tools",
            "__end__": "clear_micro_news_messages"
        }
    )
    workflow.add_edge("micro_news_tools", "micro_news_analyst")
    workflow.add_edge("clear_micro_news_messages", "fundamental_news_analyst")

    # ---------------------------------------------------------
    # 기업 뉴스 분석가(Fundamental News Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "fundamental_news_analyst",
        should_continue,
        {
            "tools": "fundamental_news_tools",
            "__end__": "clear_fundamental_news_messages"
        }
    )
    workflow.add_edge("fundamental_news_tools", "fundamental_news_analyst")
    workflow.add_edge("clear_fundamental_news_messages", "final_analyst")

    # ---------------------------------------------------------
    # 최종 분석가(Final Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "final_analyst",
        should_continue,
        {
            "tools": "final_tools",
            "__end__": "report_analyst"
        }
    )
    workflow.add_edge("final_tools", "final_analyst")
    workflow.add_edge("report_analyst", END)
    
    return workflow.compile()

# 컴파일된 그래프 싱글톤
graph = create_trading_graph()
