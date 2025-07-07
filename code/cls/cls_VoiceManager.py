"""
env name pokemon
written by DeepSeek 

Voice Manager 主管文生语音相关内容，支持非阻塞打断。
"""

import pyttsx3
import threading
import pythoncom
import time
from queue import Queue

"""
[主线程] speak() 
  │
  ↓ 添加任务
[队列] ──→ [工作线程] _process_queue()
               │
               ↓ 取出任务
           初始化引擎 → 设置回调 → 开始播放
               │
               ↓ 检测到停止?
           停止引擎 → 清理资源
"""

class VoiceManager:
    def __init__(self):
        self._queue = Queue()
        self._stop_event = threading.Event()
        self._active_engine = None
        self._lock = threading.Lock()
        
        # 启动工作线程
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._worker_thread.start()

    def speak(self, text, interrupt=True):
        """线程安全的语音播放方法"""
        with self._lock:
            if interrupt:
                self._stop_playback()  # 停止当前播放
                self._queue.queue.clear()  # 清空队列
            
            self._queue.put(text)  # 添加新语音

    def _stop_playback(self):
        """安全停止当前播放"""
        self._stop_event.set()
        if self._active_engine:
            try:
                self._active_engine.stop()
                self._active_engine.endLoop()
            except:
                pass
            finally:
                self._active_engine = None

    def _process_queue(self):
        """工作线程主循环"""
        pythoncom.CoInitialize()
        
        try:
            while True:
                self._stop_event.clear()
                text = self._queue.get()
                
                try:
                    with self._lock:
                        self._active_engine = pyttsx3.init()
                        self._active_engine.setProperty('rate', 200)
                    
                    # 注册停止检测回调
                    def on_word(name, location, length):
                        if self._stop_event.is_set():
                            self._active_engine.stop()
                            raise RuntimeError("Playback interrupted")
                    
                    self._active_engine.connect('started-word', on_word)
                    self._active_engine.say(text)
                    self._active_engine.runAndWait()
                    
                except RuntimeError:
                    pass  # 正常中断
                except Exception as e:
                    print(f"语音错误: {e}")
                finally:
                    with self._lock:
                        if self._active_engine:
                            try:
                                self._active_engine.disconnect_all()
                                self._active_engine = None
                            except:
                                pass
                    self._queue.task_done()
                    
        finally:
            pythoncom.CoUninitialize()

    def __del__(self):
        self._stop_playback()
        self._queue.join()