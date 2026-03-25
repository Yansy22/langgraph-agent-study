import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage

# 0. .env 파일의 환경 변수를 로드합니다.
load_dotenv()

# 1. 상태(State) 정의: 그래프가 공유할 데이터 구조
class State(TypedDict):
    # messages 리스트에 새로운 메시지를 계속 추가(append)하는 방식
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]

# 2. 모델 초기화 (Gemini API 키 입력 필요)
os.environ["GOOGLE_API_KEY"] = "[ENCRYPTION_KEY]"
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 3. 첫 번째 노드: 분석가 (Researcher)
def research_node(state: State):
    print("--- 분석가 작업 중 ---")
    user_query = state["messages"][-1].content
    # 분석가는 핵심 키워드를 추출하거나 기초 조사를 한다고 가정
    prompt = f"다음 주제에 대해 핵심 요약과 분석 포인트 3개를 정리해줘: {user_query}"
    response = model.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

# 4. 두 번째 노드: 작성자 (Writer)
def writer_node(state: State):
    print("--- 작성자 작업 중 ---")
    # 분석가가 내놓은 결과(마지막 메시지)를 바탕으로 최종 답변 작성
    research_result = state["messages"][-1].content
    prompt = f"다음 분석 내용을 바탕으로 일반인이 이해하기 쉽게 최종 보고서를 작성해줘:\n\n{research_result}"
    response = model.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

# 5. 그래프 구성
workflow = StateGraph(State)

# 노드 등록
workflow.add_node("researcher", research_node)
workflow.add_node("writer", writer_node)

# 흐름(Edge) 설정
workflow.set_entry_point("researcher")  # 시작은 분석가부터
workflow.add_edge("researcher", "writer") # 분석가 다음은 작성자
workflow.add_edge("writer", END)         # 작성자가 끝나면 종료

# 컴파일 (실행 가능한 앱으로 변환)
app = workflow.compile()

# 실행
inputs = {"messages": [HumanMessage(content="엔비디아 주가 전망에 대해 알려줘")]}
for event in app.stream(inputs):
    print(event) # 각 단계에서 어떤 데이터가 오가는지 확인 가능