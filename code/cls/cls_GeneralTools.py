'''
把md格式的文本改成纯文本
'''
import re
from IPython.display import Markdown, display

def markdown_to_text_simple(md_text, test_flag = True):
    if test_flag:
        return md_text
    # 移除标题标记
    text = re.sub(r'^(#+)\s+', '', md_text, flags=re.M)
    # 移除粗体/斜体
    text = re.sub(r'\*\*?([^*]+)\*\*?', r'\1', text)
    # 移除链接
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 移除图片
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    # 移除引用标记
    text = re.sub(r'^>\s+', '', text, flags=re.M)
    # 移除代码块
    text = re.sub(r'`{3}[\s\S]*?`{3}', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 仅移除无序列表标记（保留有序列表）
    text = re.sub(r'^(-|\*) ', '', text, flags=re.M)
    # 移除水平线
    text = re.sub(r'^---+$', '', text, flags=re.M)
    return text

def show_markdown(content):
    display(Markdown(content))

import json
def parse_status_json(status_str):
    status_str = status_str.replace("：", ":")
    status_str = status_str.replace("“", "\"").replace("”", "\"")
    
    """安全解析JSON字符串"""
    if not status_str or not isinstance(status_str, str):
        return None
    
    try:
        data = json.loads(status_str.strip())
        if not isinstance(data, dict):
            print("JSON数据不是字典格式")
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"无效的JSON格式: {e}")
        return None
    except Exception as e:
        print(f"解析出错: {e}")
        return None


from datetime import datetime
import os
import pyttsx3
import threading
import pythoncom
import time
from queue import Queue
def speak(text,record_necessary=False, read_necessary = True, output_file='voice', speak_rate = 250):
    file_name = f'output {datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3'
    file_path = os.path.join(output_file, file_name)
    engine = pyttsx3.init()
    engine.setProperty('rate', speak_rate)
    if record_necessary:
        engine.save_to_file(text, file_path)
    if read_necessary:
        engine.say(text)  # 直接发送语音指令
    engine.runAndWait()  # 阻塞直到播放完成