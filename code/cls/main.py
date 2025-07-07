from cls_VoiceManager import VoiceManager
from cls_ModelManager import Model_Checker
from cls_ModelManager import Agent_Manager
from cls_FileManager import File_Manager
import cls_GeneralTools 
import time
from pathlib import Path

import os

root_path = 'f:/Desktop/AI_TRPG'
fileManager = File_Manager()
rule_name = 'VHS_PROMPT.txt'
story_name = 'THE_FOX.txt'
rule = fileManager.read_file(os.path.join(root_path, 'data', 'PROMPT','RULE', rule_name) , print_flag=True)
background = fileManager.read_file(os.path.join(root_path, 'data', 'STORY', story_name) , print_flag=True)
api_key = 'sk-4f981422c9134f0796863adc193c1876'

am = Agent_Manager(api_key,rule,background)

import tkinter as tk
from tkinter import scrolledtext
import markdown
from tkhtmlview import HTMLLabel
from threading import Thread
import cls_GeneralTools
import cls_VoiceManager
import json

class StreamDisplayApp:
    def __init__(self, root, agentManager):
        self.test_mode = False
        self.root = root
        self.root.title("AI TRPG Manager by Gustaf Guo")
        self.root.geometry("1000x600")
        self.agentManager = agentManager
        self.voiceManager = cls_VoiceManager.VoiceManager()
        self.streaming = False
        self.full_response = ""
        self.history = []
        self.setup_ui()
        self.window_init()
        

    def setup_ui(self):
        # 配置根窗口网格布局
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)  # 状态栏行
        self.root.grid_rowconfigure(2, weight=0)  # 复选框行

        # 左侧框架（主容器）
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(0, weight=0)  # 输入区域（固定高度）
        left_frame.grid_rowconfigure(1, weight=1)  # 回复区域（可扩展）
        left_frame.grid_columnconfigure(0, weight=1)  # 单列填充

        # 右侧框架 - 上下两部分
        right_frame = tk.Frame(self.root)
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)  # 历史记录区域
        right_frame.grid_rowconfigure(1, weight=0)  # 玩家状态区域固定高度
        right_frame.grid_columnconfigure(0, weight=1)

        # 右上部分 - 历史记录区域
        history_frame = tk.Frame(right_frame)
        history_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        history_frame.grid_rowconfigure(1, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(history_frame, text="历史记录：").grid(row=0, column=0, sticky="w")
        self.history_label = HTMLLabel(history_frame, html="", wrap=tk.WORD)
        self.history_label.grid(row=1, column=0, sticky="nsew")

        # 右下部分 - 玩家状态表格
        status_frame = tk.Frame(right_frame, bd=2, relief=tk.GROOVE)
        status_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))  
        status_frame.config(height=200)
        
        tk.Label(status_frame, text="玩家状态", font=('Arial', 20, 'bold')).pack(pady=5)
        
        # 创建玩家状态表格
        self.player_status_table = tk.Frame(status_frame)
        self.player_status_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化状态表格
        if self.test_mode:
            initial_status = {
                "生命状态": "测试1测试2测试3测试4测试5测试6测试7测试8测试9测试10测试",
                "恐惧程度": "测试1测试2测试3测试4测试5测试6测试7测试8测试9测试10测试",
                "生理状态": "测试1测试2测试3测试4测试5测试6测试7测试8测试9测试10测试",
                "NPC队友": "测试1测试2测试3测试4测试5测试6测试7测试8测试9测试10测试",
                "背包物品": "测试1测试2测试3测试4测试5测试6测试7测试8测试9测试10测试"
            }
        else:
            initial_status = {
                "生理状态": "好的一比",
                "恐惧程度": "完全不怂",
                "NPC队友": "孤家寡人",
                "背包物品": "身手纸钥钱",
                "对怪物的认知":"丈二和尚"
            }
        self.status = initial_status
        self.update_player_status(initial_status)

        # 输入区域
        left_top_frame = tk.Frame(left_frame)
        left_top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        left_top_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(left_top_frame, text="玩家输入：").grid(row=0, column=0, sticky="w")
        self.input_text = scrolledtext.ScrolledText(left_top_frame, wrap=tk.WORD, height=8)
        self.input_text.grid(row=1, column=0, sticky="ew")
        self.input_text.bind("<Return>", self.on_enter)

        # 回复显示区域
        left_bottom_frame = tk.Frame(left_frame)
        left_bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        left_bottom_frame.grid_rowconfigure(1, weight=1)
        left_bottom_frame.grid_columnconfigure(0, weight=1)

        tk.Label(left_bottom_frame, text="主持人：").grid(row=0, column=0, sticky="w")
        self.reply_label = HTMLLabel(left_bottom_frame, html="", wrap=tk.WORD)
        self.reply_label.grid(row=1, column=0, sticky="nsew")

        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.process_button = tk.Button(button_frame, text="下一步", command=self.process_input)
        self.process_button.pack(side=tk.RIGHT)

        # 复选框
        self.checkbox_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(
            self.root,
            text="文本朗读",
            variable=self.checkbox_var,
            command=self.on_checkbox_change
        )
        checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_label = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=3, column=0, columnspan=2, sticky="ew")

    def window_init(self):
        # 初始化窗口内容
        if self.test_mode == False:
            reply = self.agentManager.show_background()
            reply_txt = cls_GeneralTools.markdown_to_text_simple(reply)
        else:
            reply = ''
            reply_txt = ''

        initial_input = "# 欢迎使用\n玩家在这里输入..."
        self.input_text.insert(tk.END, initial_input)

        initial_bottom_content = "# 这里是每轮主持人的回复，本场游戏的游戏规则如下：\n" + reply  
        initial_bottom_html = markdown.markdown(initial_bottom_content)
        self.reply_label.set_html(initial_bottom_html)

        initial_right_content = "**这里会显示所有的历史对话记录**"
        initial_right_html = markdown.markdown(initial_right_content)
        self.history_label.set_html(initial_right_html)
        
        self.root.state('zoomed')
        if self.checkbox_var.get():
            print('reading')
            self.voiceManager.speak(reply_txt)

    def on_enter(self, event):
        if event.state & 0x1:  # 检查 Shift 键是否被按下
            return
        self.process_input()
        return "break"

    def process_input(self, history=''):
        if self.streaming:
            return
            
        input_content = self.input_text.get("1.0", tk.END).strip()
        if not input_content:
            return
            
        self.streaming = True
        self.full_response = ""
        self.process_button.config(state=tk.DISABLED)
        self.status_var.set("正在获取回复...")
        
        Thread(target=self.fetch_stream_response, args=(input_content, history), daemon=True).start()

    def fetch_stream_response(self, input_content, history):
        stream_flag = True
        try:
            response = self.agentManager.talk_2_kp(prompt=input_content, stream_mode=stream_flag)
            self.root.after(0, lambda: self.safe_update_status("正在接收回复..."))  
            
            for chunk in response:
                if not self.streaming:
                    break
                    
                if hasattr(chunk, 'choices') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    self.full_response += content
                    self.root.after(0, lambda c=content: self.safe_update_reply(c)) 
            
            if self.streaming:
                self.root.after(0, lambda: self.finalize_response(history))  
                
        except Exception as e:
            self.root.after(0, lambda: self.safe_set_error(f"发生错误: {str(e)}"))  
        finally:
            self.streaming = False
            self.root.after(0, lambda: self.safe_update_buttons())  

    def finalize_response(self, history):
        reply_txt = cls_GeneralTools.markdown_to_text_simple(self.full_response,test_flag=False)
        self.agentManager.kp_history.append(self.agentManager.pack_content('assistant', reply_txt))
        # print(f'打包回传:{len(self.agentManager.kp_history)}')

        if self.checkbox_var.get():
            print('reading')
            self.voiceManager.speak(reply_txt)
        
        html_content = markdown.markdown(history + "\n\n" + self.full_response)
        self.safe_update_status("正在加载历史记录...")
        self.safe_update_history(html_content)
        
        self.safe_update_status("正在更新玩家状态...")
        new_status_str = self.agentManager.json_reply(self.status)
        print(new_status_str)
        new_status_js = cls_GeneralTools.parse_status_json(new_status_str)
        self.update_player_status(new_status_js)
        self.status = new_status_js

        self.safe_update_status("回复接收完成")

    def update_player_status(self, status_data):
        """通过JSON数据更新整个状态表格"""
        # 清空现有状态项
        for widget in self.player_status_table.winfo_children():
            widget.destroy()
        # 添加新的状态项
        for name, value in status_data.items():
            self._add_single_status_item(name, value)

    def _add_single_status_item(self, name, value):
        """内部方法：添加单个状态项到表格，自适应宽度"""
        row = tk.Frame(self.player_status_table)
        row.pack(fill=tk.X, pady=2)
        
        # 标签不再固定宽度，改为水平填充
        tk.Label(row, text=f"{name}:", anchor='w', font=('Arial', 9)).pack(side=tk.LEFT, fill=tk.X)
        tk.Label(row, text=value, anchor='w', font=('Arial', 9)).pack(side=tk.LEFT, fill=tk.X)

    def safe_update_reply(self, content):
        self.root.after(0, lambda: self.update_reply(content))

    def safe_update_history(self, html_content=None):
        """更新历史记录显示，从第二条开始显示kp_history内容"""
        history_text = ""
        
        for i, message in enumerate(self.agentManager.kp_history):
            role = message.get("role", "unknown")
            match role:
                case 'system': role = '系统'
                case 'user': role = '玩家'
                case 'assistant': role = '主持人'
                case _: pass
            
            if i < 3:  # 跳过前两条system prompt
                continue
                
            content = cls_GeneralTools.markdown_to_text_simple(message.get("content", ""))
            separator = "\n" + "─" * 50 + "\n"
            history_text += f"{separator}{role}:\n{content}\n"
        
        html_content = markdown.markdown(history_text.replace("\n", "<br>"))
        styled_html = f"""
        <div style='
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            padding: 10px;
        '>
            {html_content}
        </div>
        """
        self.root.after(0, lambda: self.history_label.set_html(styled_html))

    def safe_update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))

    def safe_set_error(self, error_msg):
        self.root.after(0, lambda: self.reply_label.set_html(
            f"<div style='color: red; padding: 10px;'>{error_msg}</div>"
        ))

    def safe_update_buttons(self):
        self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL))

    def update_reply(self, content):
        try:
            html_content = markdown.markdown(self.full_response)
            styled_html = f"""
            <div style='
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                padding: 10px;
            '>
                {html_content}
            </div>
            """
            self.reply_label.set_html(styled_html)
            self.reply_label.see(tk.END)
            self.status_var.set(f"接收中... {len(self.full_response)} 字符")
        except Exception as e:
            self.reply_label.set_html(
                f"<div style='color: red; padding: 10px;'>渲染错误: {str(e)}</div>"
            )

    def on_checkbox_change(self):
        print("复选框状态已变化:", self.checkbox_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = StreamDisplayApp(root, am)
    root.mainloop()