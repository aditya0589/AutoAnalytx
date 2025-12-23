import operator
from typing import Annotated, List, Union, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    data: Dict[str, Any] # Store loaded dataframes or metadata
    user_id: int
    session_id: str
