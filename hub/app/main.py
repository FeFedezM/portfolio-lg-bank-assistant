from typing import Union
from fastapi import FastAPI

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

import json

##import add module
import asyncio

app = FastAPI()

@app.get("/")
def read_root():

    return {"Hello": "world"}

@app.get("/stdio/list/tools/{name}")
async def list_tools(name:str):


#    async with aiofiles.open('/servers/stdio-config.json', mode='r') as file:
#        content = await file.read()
#        servers = json.loads(content)

    with open('servers/stdio-config.json', 'r') as f:
        servers = json.load(f)

    
    params = servers['mcpServers'].get(name,'')

    if not params:

        return {'error': 'Server config not found'}

    
    stdio_params = StdioServerParameters.parse_obj(params)

    async with stdio_client(stdio_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            await session.initialize()

            response = await session.list_tools()

            

            formated_tools = [dict(t) for t in response.tools]


    return formated_tools
