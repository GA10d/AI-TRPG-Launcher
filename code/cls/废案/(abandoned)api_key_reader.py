from pathlib import Path
from dotenv import load_dotenv
import os

# 读取变量
def read_api():

    # 获取当前脚本的绝对路径
    load_dotenv()  # 关键步骤！

    # 再获取环境变量
    api_key = os.getenv("API_KEY")
    print(api_key)