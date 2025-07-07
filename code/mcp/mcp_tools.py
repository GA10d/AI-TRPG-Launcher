tools = [
# {
#     "type": "function",
#     "function": {
#         "name": "get_weather",
#         "description": "获取当前城市的天气信息",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "location": {
#                     "type": "string",
#                     "description": "城市名字 e.g. 北京"
#                 },
#                 "country": {
#                     "type": "string",
#                     "description": "国家名字 e.g. 中国"
#                 }
#             },
#             "required": [
#                 "location", "coutry"
#             ],
#             "additionalProperties": False
#         }   
#     }
# },
{
    "type": "function",
    "function": {
        "name": "get_background",
        "description": "获取当前游戏的剧本信息以及背景故事",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [
            ],
            "additionalProperties": False
        }   
    }
},
{
    "type": "function",
    "function": {
        "name": "get_rule",
        "description": "获取当前游戏采用哪种TRPG规则以及规则的简要说明",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [
            ],
            "additionalProperties": False
        }   
    }
},
]