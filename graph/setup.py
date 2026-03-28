from typing import Annotated, Dict, List, Literal, TypedDict, Union
import operator

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Analyst 노드 및 데이터 레이어 임포트
from agents.analysts.market_analyst import market_analyst_node, market_analyst_instance
from agents.analysts.fundamentals_analyst import fundamentals_analyst_node, fundamentals_analyst_instance
from agents.utils.agent_state import AgentState

# --- Graph Logic ---

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """도구 호출 여부에 따라 다음 경로 결정"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 마지막 메시지에 tool_calls가 있으면 해당 도구 노드로 이동
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # 도구 호출이 없으면 현재 분석 단계를 종료하고 다음 분석가로 이동
    return "__end__"

# 전용 도구 노드 분리
# 1. 시장 분석가 전용 도구 노드
market_tools = ToolNode(market_analyst_instance.tools)
# 2. 기본적 분석가 전용 도구 노드
fundamentals_tools = ToolNode(fundamentals_analyst_instance.tools)

# --- Graph Assembly ---

# 1. 메시지 삭제 노드 정의
def clear_messages_node(state: AgentState):
    return {"messages": "CLEAR"}


def create_trading_graph():
    workflow = StateGraph(AgentState)
    
    # 분석가 및 전용 도구 노드 추가
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("market_tools", market_tools)
    workflow.add_node("clear_market_messages", clear_messages_node)
    
    workflow.add_node("fundamentals_analyst", fundamentals_analyst_node)
    workflow.add_node("fundamentals_tools", fundamentals_tools)
    workflow.add_node("clear_fundamentals_messages", clear_messages_node)
    
    # 진입점 설정: 시장 분석부터 시작
    workflow.set_entry_point("market_analyst")
    
    # ---------------------------------------------------------
    # 시장 분석가(Market Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "market_analyst",
        should_continue,
        {
            "tools": "market_tools",        # 도구 호출 시 전용 도구 노드로
            "__end__": "clear_market_messages" # 분석 종료 시 다음 분석가로
        }
    )
    # 도구 실행 후 다시 시장 분석가에게 복귀
    workflow.add_edge("market_tools", "market_analyst")
    workflow.add_edge("clear_market_messages", "fundamentals_analyst")
    
    # ---------------------------------------------------------
    # 기본적 분석가(Fundamentals Analyst) 흐름 정의
    # ---------------------------------------------------------
    workflow.add_conditional_edges(
        "fundamentals_analyst",
        should_continue,
        {
            "tools": "fundamentals_tools", # 도구 호출 시 전용 도구 노드로
            "__end__": "clear_fundamentals_messages" # 최종 분석 종료 시 END
        }
    )
    # 도구 실행 후 다시 기본적 분석가에게 복귀
    workflow.add_edge("fundamentals_tools", "fundamentals_analyst")
    workflow.add_edge("clear_fundamentals_messages", END)
    
    return workflow.compile()

# 컴파일된 그래프 싱글톤
graph = create_trading_graph()
