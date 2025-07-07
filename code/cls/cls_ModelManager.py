#env name pokemon
#written by Gustaf Guo 

"""
Agent Manager 是主管LLM模型的类，功能包括：

1. Agent余额查询 (Model_Checker)
2. LLM的调用(Agent_Manager)
"""

import sys
import os
import requests
from openai import OpenAI

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir) 
import constants 

class Model_Checker:
    # Model_Manager is a class that manages the models and their configurations.
    # It provides methods to get the list of models, get the model configuration, and get the balance.
    openai_url = constants.OPENAI_URL
    deepseek_url = constants.DEEPSEEK_URL
    balance_url = constants.BALANCE_URL
    
    def __init__(self, personal_key=None):
        self.personal_key = personal_key 

    @classmethod
    def get_url(cls):
        # This function returns the URL of the model manager.
        return {'openai_url':cls.openai_url,
                'deepseek_url':cls.deepseek_url,
                'balance_url':cls.balance_url}

    def get_balance(self, data_print=False):
        is_json = False
        payload={}
        headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' +  self.personal_key,
        }

        response = requests.request("GET", constants.BALANCE_URL, headers=headers, data=payload)
        try:
            data = response.json()
            is_json = True
            if data_print:
                print("data: ", data)
            return data
        except ValueError:
            is_json = False
            print("Error: Response is not JSON! Actual content:")
            print('original output: '+ response.text)
            return None


    def balance_explained(self, data, print_flag=False):
        # This function takes the balance data and returns a string explaining the balance.
        if data is None:
            return "No data available."
        else:
            try:
                if print_flag:
                    print("当前账户是否有余额可供 API 调用: " + str(data['is_available']))
                total_balance = data['balance_infos'][0].get('total_balance','Wrong Key') # 余额
                currency = data['balance_infos'][0].get('currency','Wrong Key') # 货币单位
                if print_flag:
                    print("当前账户余额: " + total_balance + " " + currency)
                return total_balance, currency
            except KeyError:
                print("KeyError: 'balance_infos' not found in the response.")
                return "KeyError: 'balance_infos' not found in the response.", None

################################################################################################
################################################################################################
################################################################################################

from openai import OpenAI
import requests
from datetime import datetime
from dataclasses import dataclass
import constants
import os
import json
import re
import pyttsx3
import threading
from time import sleep
from typing import Generator   

from cls_LogManager import Log_data, LogManager
from cls_FileManager import File_Manager
from cls_VoiceManager import VoiceManager
import cls_GeneralTools 

from pathlib import Path


from IPython.display import Markdown, display
from IPython.display import clear_output
from IPython.display import Javascript

class Agent_Manager:
    '''
    :personal_key 就是DeepSeek发的api_key
    :rule 就是本场游戏采用的TRPG规则
    :backgroundd 就是本场游戏采用的剧本
    '''
    def __init__(self, personal_key = None, rule = None, background = None):

        if personal_key is None:
            raise ValueError("personal_key must be provided")
        
        if rule is None:
            raise ValueError("rule must be provided")
        else:
            self.rule = rule
            self.kp_history = [{"role": "system","content":rule}]
        
        if background is None:
            raise ValueError("background must be provided")
        else:
            self.background = background


        self.personal_key = personal_key
        self.deepseek_url = constants.DEEPSEEK_URL
        self._client = None  #延迟初始化
        self.fileManager = File_Manager()
        self.root_path = Path(__file__).resolve().parent.parent.parent
        self.last_status = {
            "生命状态": "良好",
            "恐惧程度": "低",
            "生理状态": "良好",
            "NPC队友": "暂无",
            "背包物品": "暂无"
        }

        # self.npc_list = [] 
        # self.tools = mcp_tools.tools  
        # self.tool_manager = Tool_Manager(background)
    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(api_key=self.personal_key, base_url=self.deepseek_url)
        return self._client

    def pack_content(self, owner = 'user', content = ''):
        if owner not in ['user', 'assistant', 'system', 'tool']:
            raise ValueError("owner must be 'user', 'assistant' or 'system'")
        else:        
            return {"role": owner, "content": content}
    
    def clear_history(self):
        self.kp_history = self.kp_history[0:1]  #保留系统消息和第一个用户消息


    def get_reply(self,temp = 1.2):
        '''
        非流式传输，可以使用MCP工具箱
        '''
        response = self.client.chat.completions.create(
        model="deepseek-chat",
        messages=self.kp_history,
        # tools=self.tools,            # MCP工具箱
        # tool_choice="auto",          # 自动选择工具(auto, required, none)
        stream=False,
        temperature= temp)
        reply = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls

        if tool_calls is None:
            # print("No tools were called in this response.")
            return reply
        else:
            print("Tool calls detected in the response.")
            tool_call = response.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            # print(tool_name)
            # print(tool_args)
            # print(tool_call.id)
            #调用工具
            function_call_result = self.tool_manager.tool_excute(tool_name, tool_args)
            # print(function_call_result)
            # 将 function call 的结果返回给 LLM
            temp_message = [response.choices[0].message]
            temp_message.append(self.pack_tool_content(function_call_result, tool_call))
            # 再次调用 LLM
            res = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=self.kp_history+temp_message,
            )
            return res.choices[0].message.content
    

    def show_background(self):
        bg_prompt_path = os.path.join(self.root_path, 'data', 'PROMPT','FUNCTION', 'BEGINNING_PROMPT.txt')
        bg_prompt = self.fileManager.read_file(bg_prompt_path)
        
        self.kp_history.append(self.pack_content('system', self.background))
        reply = self.talk_2_kp(prompt = bg_prompt, stream_mode = False)
        return reply
    
    def talk_2_kp(self, prompt = '', record_necessary = True, stream_mode = False):
        prompt = cls_GeneralTools.markdown_to_text_simple(prompt)
        self.kp_history.append(self.pack_content('user', prompt))

        if stream_mode:
            response = self.stream_reply()
            print('成功拿到流式传输response')
        else:
            reply = self.get_reply()

        # 如果record_necessary为False，则不记录这次对话
        if record_necessary == False:
            self.kp_history.pop()
        else:    
            if stream_mode:
                pass
                #如果是流式传输无法立刻拿到完整的reply，需要从外部解析然后回传。
            else:
                reply_txt = cls_GeneralTools.markdown_to_text_simple(reply)
                self.kp_history.append(self.pack_content('assistant', reply_txt))


        if stream_mode:
            return response
        else:
            return reply
    
    def json_reply(self, last_status ,temp = 0.9,  ):
        json_prompt = """
        请你根据上一阶段的玩家信息以及这一阶段的剧情推进，严格按照以下JSON格式响应：{"生理状态": "良好", "恐惧程度": "低","NPC队友": "暂无", "背包物品": "暂无","对怪物的认知"："暂无"}推导出当前的玩家信息，注意回答要简短、表意明确。
        "生理状态"指玩家在身体上有没有受伤，例如玩家如果左腿收到伤害，则可回传"左腿骨折"这类的词语，并且如果玩家没有采取特别措施的话则不发生变化，除非剧情里有治疗骨折的操作，还要看符不符合逻辑。
        "恐惧程度"指玩家的心理状态，如果剧情显示玩家有明显的恐惧表现，或者鬼神直接显灵则会提升玩家的恐惧程度；相反，如果玩家采取措施，则会降低恐惧程度。
        "NPC队友"指玩家认识的NPC，若果有就填写，可见要标注其特征，例如"美式甜心"或者"体育生"之类的，具体情况具体分析。
        "背包物品"指玩家现在有的物品，罗列即可，若剧情无明显的对物品的增减操作，则不改变，例如："我使用手机"，则物品栏还是有手机。但是要注意如果是可消耗物品，则要有所体现，例如"吃一半巧克力"，则物品栏里的"巧克力"要变成"半块巧克力"，若是吃完则直接移除巧克力。
        "对怪物的认知"指玩家对最终boss的认知，一开始肯定是"毫无头绪"，但随着对剧情的了解，慢慢玩家会构建对怪物的认识，例如在中期可能知道它是"实体"或者"鬼魂"，在后期则有机会完全知道其名字以及特征、弱点，具体情况具体法分析。
        接下来是上一阶段的玩家信息:
        """
        last_story = self.kp_history[-2:]
        final_prompt = f'{json_prompt}  {last_status} 当前剧情是：{last_story}'
        message = self.pack_content(owner = 'system',content=final_prompt)
        print(message)
        response = self.client.chat.completions.create(
        model="deepseek-chat",
        frequency_penalty = -1,
        response_format={"type": "json_object"},
        messages=[message],
        stream=False,
        temperature= temp)
        print('get new player status')
        reply = response.choices[0].message.content
        return reply


    def md(self, content):
        cls_GeneralTools.show_markdown(content)
    

    def stream_reply(self, temp=1.2):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.kp_history,
            # tools=self.tools,
            # tool_choice="auto",
            stream=True,
            temperature=temp
        )

        return response

    def get_history(self):
        return self.kp_history
#待开发
"""

    def pack_tool_content(self, function_call_result, tool_call):
        '''
        MCP工具访问
        '''
        return {
            "role": "tool",
            "content": function_call_result,
            "tool_call_id": tool_call.id
        }
    
    def summary_history(self, distill_necessary = False):
        # self.kp_history.append(prompt_config.SUMMARY_CONFIG)
        # reply = self.get_reply()
        # if distill_necessary:
        #     self.clear_history()
        #     self.kp_history.append(self.pack_content('assistant', reply))
        # else:
        #     self.kp_history.pop()
        # return reply
        pass
        
    def stream_reply(self, temp=1.2):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.kp_history,
            # tools=self.tools,
            # tool_choice="auto",
            stream=True,
            temperature=temp
        )

        # 流式模式处理
        if isinstance(response, Generator):  # 使用 Generator 类型
            full_content = ""
            tool_calls_detected = False
            tool_call_data = None

            for chunk in response:
                # 检查是否有工具调用
                if chunk.choices[0].delta.tool_calls:
                    tool_calls_detected = True
                    tool_call_data = chunk.choices[0].delta.tool_calls[0]
                
                # 收集内容
                content = chunk.choices[0].delta.content or ""
                full_content += content
                
                # 实时 yield 内容（供外部逐段显示）
                yield content, None  # (content, tool_call)

            # 如果检测到工具调用
            if tool_calls_detected and tool_call_data:
                # 执行工具调用逻辑
                tool_name = tool_call_data.function.name
                tool_args = json.loads(tool_call_data.function.arguments)
                function_result = self.tool_manager.tool_excute(tool_name, tool_args)
                
                # 准备第二次请求
                temp_message = [{
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call_data]
                }]
                temp_message.append(self.pack_tool_content(function_result, tool_call_data))
                
                # 第二次请求（非流式）
                res = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=self.kp_history + temp_message,
                    stream=False
                )
                yield res.choices[0].message.content, None
        else:
            # 非流式模式原有逻辑
            reply = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls
            
            if not tool_calls:
                return reply, response.response
            else:
                # 处理工具调用
                tool_call = response.choices[0].message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                function_result = self.tool_manager.tool_excute(tool_name, tool_args)
                
                temp_message = [response.choices[0].message]
                temp_message.append(self.pack_tool_content(function_result, tool_call))
                
                res = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=self.kp_history + temp_message,
                    stream=False
                )
                return res.choices[0].message.content, response
"""