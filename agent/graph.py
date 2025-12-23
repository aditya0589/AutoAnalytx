import os
from typing import Annotated, Literal

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import get_tools
from agent.prompts import SYSTEM_PROMPT

def get_agent_graph(api_key: str, dataframes: dict, shared_state: dict):
    """Builds and returns the LangGraph agent."""
    
    if not api_key:
        raise ValueError("Groq API Key is required.")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0,
        streaming=True
    )

    # Get tools with injected context
    tools = get_tools(dataframes, shared_state)

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        messages = state['messages']
        # We can inject data context into the system prompt or as a message here if needed
        # For now, we rely on the tools having access to the data in the REPL
        
        # Add system prompt if it's the first message or ensure it's there
        # Actually, let's just prepend the system prompt to the messages list for the LLM call
        # or use a ChatPromptTemplate.
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | llm_with_tools
        response = chain.invoke({"messages": messages})
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()
