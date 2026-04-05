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
    micro_news_report: str
    fundamental_news_report: str
    final_decision: str
    full_decision_report: str
    ticker: str
    date: str


def get_model_content_text(content: Union[str, List[Union[str, Dict]]]) -> str:
    """
    모델 응답의 content가 문자열일 수도 있고, 
    그라운딩 서명(signature) 등 메타데이터가 포함된 리스트일 수도 있으므로,
    순수 텍스트만 추출하여 반환합니다.
    """
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            # 그 외 'extras', 'signature' 등은 텍스트가 아니므로 무시
        return "".join(text_parts)
    
    return str(content)