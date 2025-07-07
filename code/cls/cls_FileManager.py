"""
env name pokemon
written by Gustaf Guo 
"""
import os
class File_Manager:
    def __init__(self):
        pass
    def read_file(self, file_name, print_flag=True):
        try:
            with open(file_name, 'r') as file:
                if print_flag:
                    print(f"\n成功读取文件：{file_name}")
                return file.read()
        except FileNotFoundError:
            print(f"File {file_name} not found.")
            return None

    def get_txt_files(folder_path): #用作后续不同的TRPG规则的适配
        return (f for f in os.listdir(folder_path) if f.endswith('.txt'))
