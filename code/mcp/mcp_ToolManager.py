#env name pokemon
#written by Gustaf Guo 
from IPython.display import Markdown, display
from IPython.display import clear_output
from IPython.display import Javascript
from openai import OpenAI
import requests
from datetime import datetime
from dataclasses import dataclass
import constants
import prompt_config
import os
import json
import re
import pyttsx3
import threading
from time import sleep

from cls_GameLog import Log_data, GameLog
from cls_ModelChecker import Model_Checker
import mcp_tools
import mcp_functions

class Tool_Manager:
    def __init__(self,background=None,rule = None):
        if background is None:
            self.background = prompt_config.BG_CONFIG['content']
        else:
            self.background = background
        
        if rule is None:
            self.rule = prompt_config.KP_CONFIG_DOUBAO['content']
        else:
            self.rule = rule

        self.tool_list = mcp_tools.tools
        self.mcp_functions = mcp_functions.MCP_Functions()

    def tool_excute(self, tool_name, tool_args):
        print(f"Tool Manager: Executing tool {tool_name} with args {tool_args}")
        match tool_name:
            case 'get_background':
                return self.mcp_functions.get_background(self.background)
            case 'get_rule':
                return self.mcp_functions.get_rule(self.rule)
            case _:
                raise ValueError(f"Tool {tool_name} not recognized.")