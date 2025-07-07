class MCP_Functions:
    def __init__(self):
        pass

    def get_background(self, background=None):
        """
        获取当前TRPG的剧本信息
        :param background: 剧本信息
        :return: 剧本信息
        """
        return background or "当前TRPG剧本信息未提供。"

    def get_rule(self, rule=None):
        """
        获取当前TRPG的规则信息
        :param rule: 规则信息
        :return: 规则信息
        """
        return rule or "当前TRPG规则信息未提供。"
    
    # def get_weather(self, location=None, country=None):
    #     # """
    #     # 获取当前城市的天气信息
    #     # :param location: 城市名字 e.g. 北京
    #     # :param country: 国家名字 e.g. 中国
    #     # :return: 天气信息
    #     # """
    #     if not location or not country:
    #         return "请提供城市和国家信息。"
        
    #     # 模拟天气信息返回
    #     return f"{location} 的天气是晴天，温度25°C。"
