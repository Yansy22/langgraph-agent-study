from typing import Annotated, Dict, List, Optional, TypedDict, Union
import operator

def merge_messages(left: List[Dict], right: Optional[Union[List[Dict], str]]):
    # 만약 "CLEAR"라는 신호가 들어오면 메시지 리스트를 비웁니다.
    if right == "CLEAR":
        return []
    # 그 외에는 기존처럼 메시지를 추가합니다.
    return left + (right if isinstance(right, list) else [])


class AgentState(TypedDict):
    # 'messages'를 operator.add를 사용하여 계속 누적되도록 설정
    messages: Annotated[List[Dict], merge_messages]
    market_report: str
    fundamental_report: str
    ticker: str
    date: str