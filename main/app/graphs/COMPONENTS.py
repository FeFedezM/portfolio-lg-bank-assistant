from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Literal
import requests
import os
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, ToolCall
from pydantic import BaseModel



def get_tools(server_name:str , transport:str='stdio', hub_url:str | None = None, timeout:float = 5.0) -> list:
    """
    Get the the server tools from the hub
    
    Args:
        server_name: the name of the MCP server
        transport: the transport type (default stdio, Streamable SSE)
        hub_url: the base url for the hub like http://hub:80/. defualt fetch from env var HUB_URL
        timeout: the timeout for the request
    """
    #Get the base url from the variables if not provided
    if hub_url is None:
        hub_url = os.getenv('HUB_URL')

    url = f"{hub_url.rstrip('/')}/{transport}/list/tools/{server_name}"

    res = requests.get(url=url, timeout=timeout)

    if res.status_code != 200:
        raise Exception(f"Error status code: {res.status_code} detail: {res.text})")

    return res.json()


def MCP_TOOL_NODE_GENERATOR(server_name:str , transport:str='stdio', hub_url = None):

    if hub_url is None:
        hub_url = os.getenv('HUB_URL')
    
    url = f"{hub_url.rstrip('/')}/{transport}/call/tools/{server_name}"


    def TOOL_NODE(state: MessagesState):

        tool_calls = state['messages'][-1].tool_calls

        parsed_tools_calls = [{'name':t['name'], 'arguments':t['args']} for t in tool_calls]

        res =  requests.post(url, json=parsed_tools_calls)

        if res.status_code != 200:
            raise Exception(f"Error status code: {res.status_code} detail: {res.text})")
        
        parsed_tool_responses = []

        for i,  tool_respons in enumerate(res.json()):
            
            id = tool_calls[i]['id']
            content = ''
            name = tool_respons['name']

            if tool_respons['content'][0]['type'] == 'text':
                content  = tool_respons['content'][0]['text']

            ######## TO ADD HOW TO PROCESS OTHER DATA TYPE
        
            Tmessage = ToolMessage(content=content, name=name, tool_call_id=id)

            if tool_respons['isError']:
                Tmessage.error = 'error'

            parsed_tool_responses.append(Tmessage)

        return {'messages': parsed_tool_responses}

    return TOOL_NODE

def MCP_LLM_NODE_GENERATOR(server_name:str):

    tools = get_tools(server_name) ##TO ADD FUNCTIONALITIES FOR TE URL

    def LLM_NODE(state: MessagesState, config: RunnableConfig):

        llm_base = config['configurable']['llm']
        llm = llm_base.bind_tools(tools)

        
        response = llm.invoke(state['messages'])
        response.content = response.content.split("</think>\n\n")[-1]

        return {'messages': response}  
    
    return LLM_NODE

def MCP_EDGE_GENERATOR(server_name, tool_node: str = None, destination_node:str = END):

    if tool_node is None:
        tool_node = f'{server_name.upper()}_TOOL_NODE'

    def MCP_TOOL_EDGE(state: MessagesState):

            if state['messages'][-1].tool_calls:
                return tool_node
            
            return destination_node
    
    MCP_TOOL_EDGE.__annotations__['return'] = Literal[tool_node, destination_node]

    
    return MCP_TOOL_EDGE

