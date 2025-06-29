"""
This File is a custom library with utilities for using the HUB API

    Is structures is the following 
        1.- Libaries
        2.- Datastructures (Basemodels)
        3.- Classes
        4.- Functions
        5.- API Dependencies
"""
################################################################################################################################################################################################################
#      LIBRARIES
################################################################################################################################################################################################################

#For FASTAPI
from fastapi import Depends, HTTPException

#For async progrmming
import asyncio
import aiofiles
from contextlib import AsyncExitStack

#For Json
import json

#For Data structures
from typing import Annotated
from pydantic import BaseModel

#For MCP client
from mcp import StdioServerParameters
from mcp.types import CallToolResult

 

################################################################################################################################################################################################################
#     FUNCTIONS 
################################################################################################################################################################################################################




################################################################################################################################################################################################################
#     DATASTRUCTURES   
################################################################################################################################################################################################################
   
class CalledTool(BaseModel):

    name: str 
    arguments: dict

class CallToolResultWName(CallToolResult):
    """An extention of the MCP CallToolResult data structure, but adding the name of the called tool"""

    name: str

################################################################################################################################################################################################################
#     CLASSES
################################################################################################################################################################################################################

class json_loader:

    def __init__(self, path_to_json: str):
        self.path = path_to_json

    async def aGetJson(self):
        async with aiofiles.open(self.path, mode='r') as file:
            content = await file.read()
        return json.loads(content)
    
    async def __aenter__(self):
        servers = await self.aGetJson()
        return servers
    
################################################################################################################################################################################################################
#     DEPENDENCIES
################################################################################################################################################################################################################

#stdio Client dependency
async def get_stdio_params(name: str):

    loader = json_loader('servers/stdio-config.json')
        
    servers = await loader.aGetJson()

    
    params = servers['mcpServers'].get(name,'')

    if not params:

        raise HTTPException(status_code=404, detail="Server not found")

    
    stdio_params = StdioServerParameters.parse_obj(params)

    return stdio_params
 
DepStdioParams = Annotated[dict,Depends(get_stdio_params)]


