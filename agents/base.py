import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from agents.utils.agent_state import get_model_content_text
from agents.rules import GLOBAL_CONSTITUTION

class BaseAnalyst(ABC):
    """
    모든 분석가 에이전트의 기반이 되는 추상 클래스입니다.
    """
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        self._llm = None
        self._llm_with_tools = None

    @property
    def llm(self):
        if self._llm is None:
            # 환경 변수가 로드된 후(execute 시점) 생성되도록 함
            self._llm = ChatGoogleGenerativeAI(model=self.model_name)
        return self._llm

    @property
    def llm_with_tools(self):
        if self._llm_with_tools is None:
            # 도구가 있다면 바인딩, 없다면 일반 LLM 사용
            tools = self._get_tools()
            if tools:
                self._llm_with_tools = self.llm.bind_tools(tools)
            else:
                self._llm_with_tools = self.llm
        return self._llm_with_tools

    @property
    def tools(self):
        return self._get_tools()

    @abstractmethod
    def _get_tools(self) -> List:
        """에이전트가 사용할 도구 목록을 반환합니다."""
        pass

    @abstractmethod
    def _get_system_prompt(self, state: Dict) -> str:
        """에이전트의 시스템 프롬프트를 반환합니다."""
        pass

    @abstractmethod
    def _get_bylaws(self) -> str:
        """에이전트의 도메인별 부칙(Bylaws)을 반환합니다."""
        pass

    @abstractmethod
    def _get_report_key(self) -> Optional[str]:
        """분석 결과 보고서를 저장할 State의 키(Key)를 반환합니다."""
        pass

    def _get_human_message(self, state: Dict) -> str:
        """에이전트에게 전달할 첫 지시 메시지입니다. 필요 시 오버라이드 가능합니다."""
        ticker = state.get("ticker", "NVDA")
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))
        return f"Please perform an analysis for {ticker} on {date}."

    def execute(self, state: Dict) -> Dict:
        """
        LangGraph 노드에서 호출될 실제 실행 로직입니다.
        """
        messages = state.get("messages", [])
        ticker = state.get("ticker", "UNKNOWN")
        
        # 에이전트 이름 추출 (로깅용)
        agent_name = self.__class__.__name__
        print(f"\n[{agent_name}] Processing for {ticker}...")

        # 1. 메시지 히스토리가 비어있다면 사용자 질문 생성
        new_messages = []
        if not messages:
            start_msg = HumanMessage(content=self._get_human_message(state))
            messages = [start_msg]
            new_messages.append(start_msg)

        # 2. 프롬프트 구성 (Constitution + Bylaws + Base Prompt)
        date = state.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # 규칙 주입
        constitution = GLOBAL_CONSTITUTION
        bylaws = self._get_bylaws()
        base_prompt = self._get_system_prompt(state)
        
        system_prompt = (
            f"{constitution}\n\n"
            f"{bylaws}\n\n"
            f"## Task Specific Instructions\n"
            f"{base_prompt}\n\n"
            f"Target: {ticker}, Date: {date}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # 3. LLM 호출
        chain = prompt | self.llm_with_tools
        result = chain.invoke({"messages": messages})
        
        # 4. 반환값 구성 (새로 생성된 메시지들 모두 저장)
        new_messages.append(result)
        res = {"messages": new_messages}
        
        # 5. 도구 호출이 없는 경우(최종 보고서가 생성된 경우) 지정된 키에 결과 저장
        if not (hasattr(result, "tool_calls") and result.tool_calls):
            print(f"[{agent_name}] Final report generated.")
            report_key = self._get_report_key()
            if report_key:
                content = get_model_content_text(result.content)
                res[report_key] = content
                print(f"[{agent_name}] Saved report to state['{report_key}']. Length: {len(content)}")
        else:
            print(f"[{agent_name}] Tool calls detected: {[tc['name'] for tc in result.tool_calls]}")
            
        return res


    def to_node(self):
        """
        LangGraph에 등록할 수 있는 노드 함수 형식을 반환합니다.
        """
        def node(state: Dict):
            return self.execute(state)
        return node
