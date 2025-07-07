"""
env name pokemon
written by Gustaf Guo 

Log Manager 主管游戏过程中的日志生成、存储以及查询。
"""

from datetime import datetime
from dataclasses import dataclass
import os

@dataclass(order=True)

class Log_data:
    start_time: str 
    time: str
    owner: str
    content: str

class LogManager:
    def __init__(self):
        self.game_log = []          #存储游戏运行的日志
        self.story_log = []         #存储故事内容
        self.total_log = []         #存储全部内容（上述两者）

        self.current_file = os.path.dirname(__file__)
        self.cls_dir = os.path.dirname(self.current_file) 
        self.code_dir = os.path.dirname(self.cls_dir) 

        self.gamelog_path = os.path.join(self.code_dir,'log','game_log.txt')
        self.storylog_path = os.path.join(self.code_dir,'log','story_log.txt')
        self.totallog_path = os.path.join(self.code_dir,'log','total_log.txt') 

        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #项目启动时间

    def update_log(self, content = '', owner='system',mode = 'total'):
        """
        上传一条log
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temp_log = Log_data(self.start_time, current_time, owner, content)

        match mode:
            case 'game':
                self.game_log.append(temp_log)
                self.total_log.append(temp_log)
            case 'story':
                self.story_log.append(temp_log)
                self.total_log.append(temp_log)
            case 'total':
                self.total_log.append(temp_log)
            case _:
                raise ValueError("Invalid mode. Use 'total', 'game' or 'story'.")
        
    def clear_log(self, log):
        """
        调用时log需要传回GameLog的属性,例如GameLog.game_log
        """
        log.clear()

    def query_log(self, num2print: int = -1, mode: str = 'total'):
        """
        查询游戏日志，支持控制打印最后几条
        :param num2print: 打印的日志数量，-1表示全部打印
        """
        match mode:
            case 'game':
                log = self.game_log
                name = '游戏'
            case 'story':
                log = self.story_log
                name = '故事'
            case 'total':
                log = self.total_log
                name = '总'
            case _:
                raise ValueError("Invalid mode. Use 'total', 'game' or 'story'.")
            
        if not log:
            raise ValueError(f"没有{name}日志可供打印")
        
        if num2print <= 0:
            print(f"打印{name}日志全部内容:")
            num2print = 0
        else:
            print(f"打印{name}日志最后{num2print}条内容:")
        logs_to_print = log[-num2print:] if num2print > 0 else self.game_log
        for s in logs_to_print:
            print(f"[{s.start_time}] >> [{s.owner}]: {s.content}")

    def get_log_from(self, owner = 'system', mode = 'total'):
        """
        获取指定玩家的日志
        :param owner: 玩家名称
        :param mode: 日志类型，'total', 'game' 或 'story'
        :return: 指定玩家的日志列表
        """
        match mode:
            case 'game':
                log = self.game_log
            case 'story':
                log = self.story_log
            case 'total':
                log = self.total_log
            case _:
                raise ValueError("Invalid mode. Use 'total', 'game' or 'story'.")
        
        return [s for s in log if s.owner == owner]

    def generate_log(self):
        log_configs = [
            (self.gamelog_path, self.game_log),
            (self.storylog_path, self.story_log),
            (self.totallog_path, self.total_log)
        ]
        
        for file_path, log_data in log_configs:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(
                    f"[{log.start_time}] >> [{log.owner}]: {log.content}\n"
                    for log in log_data
                )