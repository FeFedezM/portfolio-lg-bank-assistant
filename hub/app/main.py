from fastapi import FastAPI

##import add module
import asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from utilities import json_loader, DepStdioParams, CalledTool

stdio_servers =json_loader('servers/stdio-config.json')


app = FastAPI()

@app.get("/")
def read_root():

    return {"Hello": "world"}

@app.get("/playground/")
async def playground():

    return {'hi': 'hi'}

@app.get("/stdio/list/servers")
async def get_servers():

    list_of_servers: dict = await stdio_servers.aGetJson()

    
    return list(list_of_servers['mcpServers'].keys())

@app.get("/stdio/list/tools/{name}")
async def list_tools(server_params: DepStdioParams):

    if server_params == {}:
        return {'error': 'Model not foud'}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write) as session:
            # Initialize the connection
            await session.initialize()

            res = await session.list_tools()

    return res.tools        
        
@app.post("/stdio/call/tools/{name}")
async def list_tools(server_params: DepStdioParams, tools: list[CalledTool]):

    if server_params == {}:
        return {'error': 'Model not foud'}
    
    responses = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write) as session:
            # Initialize the connection
            await session.initialize()

            for tool in tools:

                try:
                    response =  await session.call_tool(name=tool.name, arguments=tool.arguments)
                    responses.append(response)
                except:
                    responses.append({'error': f"error calling tool '{tool.name}' with arguments: {tool.arguments}"})

 
    return responses       