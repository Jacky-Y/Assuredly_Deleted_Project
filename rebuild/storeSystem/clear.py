import os
import shutil

# 定义要清空的目录列表
directories_to_clear = ['c', 'd', 'e', 'f']

# 遍历每个目录
for directory in directories_to_clear:
    # 构建目录的完整路径
    dir_path = os.path.join(os.getcwd(), directory)

    # 确保目录存在
    if os.path.exists(dir_path):
        # 遍历目录中的文件和子目录
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)

            # 检查是否是.gitkeep文件
            if filename != '.gitkeep':
                # 如果是目录，则递归删除
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                # 如果是文件，则直接删除
                else:
                    os.remove(file_path)

# 删除当前目录下的local_state.json文件
local_state_path = os.path.join(os.getcwd(), 'local_state.json')
if os.path.exists(local_state_path):
    os.remove(local_state_path)

print("Cleanup completed.")
