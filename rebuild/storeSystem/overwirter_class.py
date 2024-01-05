import os
import json
import math
import shutil
import difflib
import datetime

class JsonOverwriter:
    def __init__(self, granularity, alg_param, level):
        """
        初始化 JsonOverwriter 类。
        :param granularity: 覆写的粒度（特定字段名）。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        self.granularity = granularity
        self.alg_param = alg_param
        self.level = level

    def log(self, message, level="INFO"):
        """
        简单的日志记录方法。
        :param message: 要记录的日志消息。
        :param level: 日志级别（如'INFO', 'ERROR', 'WARNING'）。
        """
        print(f"[{level}] {message}")

    def overwrite_file(self, target_files):
        """
        覆写指定的 JSON 文件。
        :param target_files: 要覆写的目标文件列表。
        """
        for file_path in target_files:
            for _ in range(self.level):
                try:
                    self._process_file(file_path)
                except Exception as e:
                    self.log(f"Error processing file {file_path}: {e}", "ERROR")
                    raise

    def _process_file(self, file_path):
        """
        处理单个文件的覆写逻辑。
        :param file_path: 要处理的文件路径。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        if self.granularity:
            self._overwrite_specific_field(file_path)
        else:
            self._overwrite_entire_file(file_path)

    def _overwrite_specific_field(self, file_path):
        """
        只覆写 JSON 文件中指定的字段。
        :param file_path: JSON 文件的路径。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if self.granularity in data:
            data[self.granularity] = self.alg_param  # 覆写该字段
        else:
            self.log(f"Field '{self.granularity}' not found in {file_path}.", "WARNING")
            return

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _overwrite_entire_file(self, file_path):
        """
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        file_size = os.path.getsize(file_path)
        write_count = math.ceil(file_size / len(self.alg_param))
        overwrite_content = self.alg_param * write_count

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(overwrite_content)
    
    def set_parameters(self, granularity, alg_param, level):
        """
        设置类的参数。
        :param granularity: 覆写的粒度（特定字段名）。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        if not isinstance(granularity, (str, type(None))):
            raise ValueError("Granularity must be a string or None.")
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.granularity = granularity
        self.alg_param = alg_param
        self.level = level

    def set_custom_overwrite_function(self, custom_function):
        """
        设置自定义覆写函数。
        :param custom_function: 一个接受文件路径作为参数并返回字符串的函数。
        """
        if not callable(custom_function):
            raise ValueError("Custom function must be callable.")
        self.custom_function = custom_function

    def clean_up(self):
        """
        执行资源清理工作。
        """
        # 示例：关闭任何打开的文件句柄
        if hasattr(self, 'file_handle') and not self.file_handle.closed:
            self.file_handle.close()
            self.file_handle = None
            print("File handle closed.")

        # 示例：删除临时文件
        if hasattr(self, 'temp_files'):
            for temp_file in self.temp_files:
                try:
                    os.remove(temp_file)
                    print(f"Temporary file {temp_file} removed.")
                except OSError as e:
                    print(f"Error removing {temp_file}: {e}")

        # 重置内部状态或其他资源
        # ...

        print("Clean-up completed.")

    def analyze_json_files(self, json_files):
            """
            分析一系列 JSON 文件，报告每个文件的统计信息。
            :param json_files: JSON 文件列表。
            """
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                        print(f"Analyzing {file_path}...")
                        self._print_file_statistics(data)

                except (IOError, json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"Error reading file {file_path}: {e}")

    def _print_file_statistics(self, data, level=0):
        """
        打印 JSON 数据的统计信息。
        :param data: JSON 数据对象。
        :param level: 当前 JSON 数据的嵌套层级。
        """
        if isinstance(data, dict):
            print(f"{' '*level}Level {level}: Object with {len(data.keys())} keys")
            for key, value in data.items():
                print(f"{' '*level}- Key '{key}': {type(value).__name__}")
                if isinstance(value, (list, dict)):
                    self._print_file_statistics(value, level + 1)
                elif isinstance(value, str):
                    if self._check_special_condition(value):
                        print(f"{' '*level}  [Special Condition Met] Value: {value}")

        elif isinstance(data, list):
            print(f"{' '*level}Level {level}: Array with {len(data)} elements")
            for item in data:
                if isinstance(item, (list, dict)):
                    self._print_file_statistics(item, level + 1)

        else:
            print(f"{' '*level}Level {level}: {type(data).__name__}")

    def _check_special_condition(self, value):
        """
        检查特殊条件是否满足。
        :param value: 要检查的字符串值。
        :return: 布尔值，表示是否满足条件。
        """
        # 这里可以定义一些特殊的检查逻辑
        return 'special_keyword' in value

    # 这里可以添加更多复杂的分析逻辑
    # 可以对数据进行更深入的分析，例如统计特定类型的字段数量，检查特定的值模式等
    # ...


class TextOverwriter:
    def __init__(self, alg_param, level):
        """
        初始化 TextOverwriter 类。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        # 参数验证
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def log(self, message, level="INFO"):
        """
        简单的日志记录方法。
        :param message: 要记录的日志消息。
        :param level: 日志级别（如'INFO', 'ERROR', 'WARNING'）。
        """
        print(f"[{level}] {message}")

    def overwrite_file(self, target_files):
        """
        覆写指定的文本文件。
        :param target_files: 要覆写的目标文件列表。
        """
        # 参数验证
        if not isinstance(target_files, list) or not all(isinstance(file, str) for file in target_files):
            raise ValueError("Target files must be a list of file paths.")

        for file_path in target_files:
            for _ in range(self.level):
                try:
                    self._process_file(file_path)
                except FileNotFoundError as e:
                    self.log(f"File not found: {file_path}", "ERROR")
                except IOError as e:
                    self.log(f"IO Error processing file {file_path}: {e}", "ERROR")
                except Exception as e:
                    self.log(f"Error processing file {file_path}: {e}", "ERROR")
                    raise

    def _process_file(self, file_path):
        """
        处理单个文件的覆写逻辑。
        :param file_path: 要处理的文件路径。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        self._overwrite_entire_file(file_path)

    def _overwrite_entire_file(self, file_path):
        """
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        # 获取文件大小并计算覆写次数
        file_size = os.path.getsize(file_path)
        write_count = math.ceil(file_size / len(self.alg_param))

        # 使用分块写入以提高大文件处理的性能
        with open(file_path, 'w', encoding='utf-8') as f:
            for _ in range(write_count):
                f.write(self.alg_param)


    def set_parameters(self, alg_param, level):
        """
        设置类的参数。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def find_and_replace(self, file_path, target_string, replacement_string):
        """
        在文件中查找并替换指定的字符串。
        :param file_path: 目标文件的路径。
        :param target_string: 要查找的字符串。
        :param replacement_string: 用于替换的字符串。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")
        if not isinstance(target_string, str) or not isinstance(replacement_string, str):
            raise ValueError("Target and replacement strings must be strings.")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            content = content.replace(target_string, replacement_string)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")

    def append_to_file(self, file_path, additional_content):
        """
        向文件末尾追加内容。
        :param file_path: 目标文件的路径。
        :param additional_content: 要追加的内容。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")
        if not isinstance(additional_content, str):
            raise ValueError("Additional content must be a string.")

        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(additional_content)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")

    def prepend_to_file(self, file_path, additional_content):
        """
        在文件开头添加内容。
        :param file_path: 目标文件的路径。
        :param additional_content: 要添加的内容。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")
        if not isinstance(additional_content, str):
            raise ValueError("Additional content must be a string.")

        try:
            with open(file_path, 'r+', encoding='utf-8') as file:
                content = file.read()
                file.seek(0, 0)
                file.write(additional_content + content)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")

    def remove_from_file(self, file_path, target_string):
        """
        从文件中移除指定的字符串。
        :param file_path: 目标文件的路径。
        :param target_string: 要移除的字符串。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")
        if not isinstance(target_string, str):
            raise ValueError("Target string must be a string.")

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 移除目标字符串
            updated_content = content.replace(target_string, "")

            # 将更新后的内容写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")


    def backup_file(self, file_path):
        """
        备份指定的文件。
        :param file_path: 要备份的文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        backup_path = file_path + ".bak"
        try:
            shutil.copy(file_path, backup_path)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")

    def restore_file(self, backup_path):
        """
        从备份恢复文件。
        :param backup_path: 备份文件的路径。
        """
        if not isinstance(backup_path, str):
            raise ValueError("Backup path must be a string.")

        original_path = backup_path.rstrip(".bak")
        try:
            shutil.copy(backup_path, original_path)
        except FileNotFoundError:
            self.log(f"Backup file not found: {backup_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {backup_path}: {e}", "ERROR")

    def analyze_file_content(self, file_path):
        """
        分析文件内容并报告统计信息。
        :param file_path: 要分析的文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 示例分析：统计字符数和行数
            num_chars = len(content)
            num_lines = content.count('\n') + 1
            self.log(f"File {file_path} has {num_chars} characters and {num_lines} lines.", "INFO")

        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")

    def compare_files(self, file_path1, file_path2):
        """
        比较两个文件的内容差异。
        :param file_path1: 第一个文件的路径。
        :param file_path2: 第二个文件的路径。
        """
        if not isinstance(file_path1, str) or not isinstance(file_path2, str):
            raise ValueError("File paths must be strings.")

        try:
            with open(file_path1, 'r', encoding='utf-8') as file1, \
                 open(file_path2, 'r', encoding='utf-8') as file2:
                content1 = file1.readlines()
                content2 = file2.readlines()

            # 使用 difflib 比较文件差异
            diffs = list(difflib.unified_diff(content1, content2, lineterm=''))
            if diffs:
                self.log(f"Differences found between {file_path1} and {file_path2}:\n" + "\n".join(diffs), "INFO")
            else:
                self.log(f"No differences found between {file_path1} and {file_path2}.", "INFO")

        except FileNotFoundError as e:
            self.log(f"File not found: {e}", "ERROR")
        except IOError as e:
            self.log(f"IO Error processing files: {e}", "ERROR")


    # 更多函数可以根据需求添加
    # ...

class VideoOverwriter:
    def __init__(self, alg_param, level):
        """
        初始化 VideoOverwriter 类。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        # 参数验证
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def log(self, message, level="INFO"):
        """
        简单的日志记录方法。
        :param message: 要记录的日志消息。
        :param level: 日志级别（如'INFO', 'ERROR', 'WARNING'）。
        """
        print(f"[{level}] {message}")

    def overwrite_file(self, target_files):
        """
        覆写指定的文本文件。
        :param target_files: 要覆写的目标文件列表。
        """
        # 参数验证
        if not isinstance(target_files, list) or not all(isinstance(file, str) for file in target_files):
            raise ValueError("Target files must be a list of file paths.")

        for file_path in target_files:
            for _ in range(self.level):
                try:
                    self._process_file(file_path)
                except FileNotFoundError as e:
                    self.log(f"File not found: {file_path}", "ERROR")
                except IOError as e:
                    self.log(f"IO Error processing file {file_path}: {e}", "ERROR")
                except Exception as e:
                    self.log(f"Error processing file {file_path}: {e}", "ERROR")
                    raise

    def _process_file(self, file_path):
        """
        处理单个文件的覆写逻辑。
        :param file_path: 要处理的文件路径。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        self._overwrite_entire_file(file_path)

    def overwrite_entire_file_previous(self, file_path):
        """
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        # 获取文件大小并计算覆写次数
        file_size = os.path.getsize(file_path)
        write_count = math.ceil(file_size / len(self.alg_param))

        # 使用分块写入以提高大文件处理的性能
        with open(file_path, 'w', encoding='utf-8') as f:
            for _ in range(write_count):
                f.write(self.alg_param)
    
    def _overwrite_entire_file(self, file_path):
        """
        经过优化的覆写方法,分块覆写
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        try:
            chunk_size = 1024 * 1024  # 例如，每块 1MB
            with open(file_path, 'rb+') as f:
                while True:
                    # 读取一小块文件
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    # 生成覆写内容
                    # 生成覆写内容，并确保长度与读取块长度一致
                    overwrite_content = (self.alg_param.encode() * (len(chunk) // len(self.alg_param.encode()) + 1))[:len(chunk)]


                    # 回到块的开始位置并覆写
                    f.seek(-len(chunk), 1)
                    f.write(overwrite_content)
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")


    def set_parameters(self, alg_param, level):
        """
        设置类的参数。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def backup_file(self, file_path):
        """
        备份指定的视频文件。
        :param file_path: 要备份的视频文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        backup_path = file_path + ".bak"
        try:
            shutil.copy(file_path, backup_path)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during backup: {e}", "ERROR")

    def restore_file(self, backup_path):
        """
        从备份中恢复视频文件。
        :param backup_path: 备份文件的路径。
        """
        if not isinstance(backup_path, str):
            raise ValueError("Backup path must be a string.")

        original_path = backup_path.rstrip(".bak")
        try:
            shutil.copy(backup_path, original_path)
        except FileNotFoundError:
            self.log(f"Backup file not found: {backup_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during restoration: {e}", "ERROR")

    def report_video_info(self, file_path):
        """
        报告视频文件的基本信息。
        :param file_path: 视频文件的路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            file_size = os.path.getsize(file_path)
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            self.log(f"File Size: {file_size} bytes, Last Modified: {modification_time}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def delete_video(self, file_path):
        """
        安全地删除视频文件。
        :param file_path: 要删除的视频文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            os.remove(file_path)
            self.log(f"File {file_path} has been deleted successfully", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def rename_video(self, file_path, new_name):
        """
        重命名视频文件。
        :param file_path: 要重命名的视频文件的当前路径。
        :param new_name: 新的文件名（不包括路径）。
        """
        if not isinstance(file_path, str) or not isinstance(new_name, str):
            raise ValueError("File path and new name must be strings.")

        new_path = os.path.join(os.path.dirname(file_path), new_name)
        try:
            os.rename(file_path, new_path)
            self.log(f"File renamed to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def move_video(self, file_path, new_path):
        """
        将视频文件移动到新位置。
        :param file_path: 要移动的视频文件的当前路径。
        :param new_path: 视频文件的新路径。
        """
        if not isinstance(file_path, str) or not isinstance(new_path, str):
            raise ValueError("File path and new path must be strings.")

        try:
            shutil.move(file_path, new_path)
            self.log(f"File moved to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def duplicate_video(self, file_path, duplicate_path):
        """
        创建视频文件的副本。
        :param file_path: 要复制的视频文件的路径。
        :param duplicate_path: 副本的路径。
        """
        if not isinstance(file_path, str) or not isinstance(duplicate_path, str):
            raise ValueError("File path and duplicate path must be strings.")

        try:
            shutil.copy(file_path, duplicate_path)
            self.log(f"File duplicated to {duplicate_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")



class AudioOverwriter:
    def __init__(self, alg_param, level):
        """
        初始化 AudioOverwriter 类。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        # 参数验证
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def log(self, message, level="INFO"):
        """
        简单的日志记录方法。
        :param message: 要记录的日志消息。
        :param level: 日志级别（如'INFO', 'ERROR', 'WARNING'）。
        """
        print(f"[{level}] {message}")

    def overwrite_file(self, target_files):
        """
        覆写指定的文本文件。
        :param target_files: 要覆写的目标文件列表。
        """
        # 参数验证
        if not isinstance(target_files, list) or not all(isinstance(file, str) for file in target_files):
            raise ValueError("Target files must be a list of file paths.")

        for file_path in target_files:
            for _ in range(self.level):
                try:
                    self._process_file(file_path)
                except FileNotFoundError as e:
                    self.log(f"File not found: {file_path}", "ERROR")
                except IOError as e:
                    self.log(f"IO Error processing file {file_path}: {e}", "ERROR")
                except Exception as e:
                    self.log(f"Error processing file {file_path}: {e}", "ERROR")
                    raise

    def _process_file(self, file_path):
        """
        处理单个文件的覆写逻辑。
        :param file_path: 要处理的文件路径。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        self._overwrite_entire_file(file_path)

    def overwrite_entire_file_previous(self, file_path):
        """
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        # 获取文件大小并计算覆写次数
        file_size = os.path.getsize(file_path)
        write_count = math.ceil(file_size / len(self.alg_param))

        # 使用分块写入以提高大文件处理的性能
        with open(file_path, 'w', encoding='utf-8') as f:
            for _ in range(write_count):
                f.write(self.alg_param)
    
    def _overwrite_entire_file(self, file_path):
        """
        经过优化的覆写方法,分块覆写
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        try:
            chunk_size = 1024 * 1024  # 例如，每块 1MB
            with open(file_path, 'rb+') as f:
                while True:
                    # 读取一小块文件
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    # 生成覆写内容
                    # 生成覆写内容，并确保长度与读取块长度一致
                    overwrite_content = (self.alg_param.encode() * (len(chunk) // len(self.alg_param.encode()) + 1))[:len(chunk)]


                    # 回到块的开始位置并覆写
                    f.seek(-len(chunk), 1)
                    f.write(overwrite_content)
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")


    def set_parameters(self, alg_param, level):
        """
        设置类的参数。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def backup_file(self, file_path):
        """
        备份指定的音频文件。
        :param file_path: 要备份的音频文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        backup_path = file_path + ".bak"
        try:
            shutil.copy(file_path, backup_path)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during backup: {e}", "ERROR")

    def restore_file(self, backup_path):
        """
        从备份中恢复音频文件。
        :param backup_path: 备份文件的路径。
        """
        if not isinstance(backup_path, str):
            raise ValueError("Backup path must be a string.")

        original_path = backup_path.rstrip(".bak")
        try:
            shutil.copy(backup_path, original_path)
        except FileNotFoundError:
            self.log(f"Backup file not found: {backup_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during restoration: {e}", "ERROR")

    def report_audio_info(self, file_path):
        """
        报告音频文件的基本信息。
        :param file_path: 音频文件的路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            file_size = os.path.getsize(file_path)
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            self.log(f"File Size: {file_size} bytes, Last Modified: {modification_time}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def delete_audio(self, file_path):
        """
        安全地删除音频文件。
        :param file_path: 要删除的音频文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            os.remove(file_path)
            self.log(f"File {file_path} has been deleted successfully", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def rename_audio(self, file_path, new_name):
        """
        重命名音频文件。
        :param file_path: 要重命名的音频文件的当前路径。
        :param new_name: 新的文件名（不包括路径）。
        """
        if not isinstance(file_path, str) or not isinstance(new_name, str):
            raise ValueError("File path and new name must be strings.")

        new_path = os.path.join(os.path.dirname(file_path), new_name)
        try:
            os.rename(file_path, new_path)
            self.log(f"File renamed to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def move_audio(self, file_path, new_path):
        """
        将音频文件移动到新位置。
        :param file_path: 要移动的音频文件的当前路径。
        :param new_path: 音频文件的新路径。
        """
        if not isinstance(file_path, str) or not isinstance(new_path, str):
            raise ValueError("File path and new path must be strings.")

        try:
            shutil.move(file_path, new_path)
            self.log(f"File moved to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def duplicate_audio(self, file_path, duplicate_path):
        """
        创建音频文件的副本。
        :param file_path: 要复制的音频文件的路径。
        :param duplicate_path: 副本的路径。
        """
        if not isinstance(file_path, str) or not isinstance(duplicate_path, str):
            raise ValueError("File path and duplicate path must be strings.")

        try:
            shutil.copy(file_path, duplicate_path)
            self.log(f"File duplicated to {duplicate_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")


class ImageOverwriter:
    def __init__(self, alg_param, level):
        """
        初始化 ImageOverwriter 类。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        # 参数验证
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def log(self, message, level="INFO"):
        """
        简单的日志记录方法。
        :param message: 要记录的日志消息。
        :param level: 日志级别（如'INFO', 'ERROR', 'WARNING'）。
        """
        print(f"[{level}] {message}")

    def overwrite_file(self, target_files):
        """
        覆写指定的文本文件。
        :param target_files: 要覆写的目标文件列表。
        """
        # 参数验证
        if not isinstance(target_files, list) or not all(isinstance(file, str) for file in target_files):
            raise ValueError("Target files must be a list of file paths.")

        for file_path in target_files:
            for _ in range(self.level):
                try:
                    self._process_file(file_path)
                except FileNotFoundError as e:
                    self.log(f"File not found: {file_path}", "ERROR")
                except IOError as e:
                    self.log(f"IO Error processing file {file_path}: {e}", "ERROR")
                except Exception as e:
                    self.log(f"Error processing file {file_path}: {e}", "ERROR")
                    raise

    def _process_file(self, file_path):
        """
        处理单个文件的覆写逻辑。
        :param file_path: 要处理的文件路径。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        self._overwrite_entire_file(file_path)

    def overwrite_entire_file_previous(self, file_path):
        """
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        # 获取文件大小并计算覆写次数
        file_size = os.path.getsize(file_path)
        write_count = math.ceil(file_size / len(self.alg_param))

        # 使用分块写入以提高大文件处理的性能
        with open(file_path, 'w', encoding='utf-8') as f:
            for _ in range(write_count):
                f.write(self.alg_param)
    
    def _overwrite_entire_file(self, file_path):
        """
        经过优化的覆写方法,分块覆写
        覆写整个文件的内容。
        :param file_path: 文件的路径。
        """
        try:
            chunk_size = 1024 * 1024  # 例如，每块 1MB
            with open(file_path, 'rb+') as f:
                while True:
                    # 读取一小块文件
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    # 生成覆写内容
                    # 生成覆写内容，并确保长度与读取块长度一致
                    overwrite_content = (self.alg_param.encode() * (len(chunk) // len(self.alg_param.encode()) + 1))[:len(chunk)]


                    # 回到块的开始位置并覆写
                    f.seek(-len(chunk), 1)
                    f.write(overwrite_content)
        except IOError as e:
            self.log(f"IO Error processing file {file_path}: {e}", "ERROR")


    def set_parameters(self, alg_param, level):
        """
        设置类的参数。
        :param alg_param: 用于覆写的字符串。
        :param level: 覆写的次数。
        """
        if not isinstance(alg_param, str):
            raise ValueError("Algorithm parameter must be a string.")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be a positive integer.")

        self.alg_param = alg_param
        self.level = level

    def backup_file(self, file_path):
        """
        备份指定的图片文件。
        :param file_path: 要备份的图片文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        backup_path = file_path + ".bak"
        try:
            shutil.copy(file_path, backup_path)
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during backup: {e}", "ERROR")

    def restore_file(self, backup_path):
        """
        从备份中恢复图片文件。
        :param backup_path: 备份文件的路径。
        """
        if not isinstance(backup_path, str):
            raise ValueError("Backup path must be a string.")

        original_path = backup_path.rstrip(".bak")
        try:
            shutil.copy(backup_path, original_path)
        except FileNotFoundError:
            self.log(f"Backup file not found: {backup_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error during restoration: {e}", "ERROR")

    def report_image_info(self, file_path):
        """
        报告图片文件的基本信息。
        :param file_path: 图片文件的路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            file_size = os.path.getsize(file_path)
            modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            self.log(f"File Size: {file_size} bytes, Last Modified: {modification_time}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def delete_image(self, file_path):
        """
        安全地删除图片文件。
        :param file_path: 要删除的图片文件路径。
        """
        if not isinstance(file_path, str):
            raise ValueError("File path must be a string.")

        try:
            os.remove(file_path)
            self.log(f"File {file_path} has been deleted successfully", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def rename_image(self, file_path, new_name):
        """
        重命名图片文件。
        :param file_path: 要重命名的图片文件的当前路径。
        :param new_name: 新的文件名（不包括路径）。
        """
        if not isinstance(file_path, str) or not isinstance(new_name, str):
            raise ValueError("File path and new name must be strings.")

        new_path = os.path.join(os.path.dirname(file_path), new_name)
        try:
            os.rename(file_path, new_path)
            self.log(f"File renamed to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def move_image(self, file_path, new_path):
        """
        将图片文件移动到新位置。
        :param file_path: 要移动的图片文件的当前路径。
        :param new_path: 图片文件的新路径。
        """
        if not isinstance(file_path, str) or not isinstance(new_path, str):
            raise ValueError("File path and new path must be strings.")

        try:
            shutil.move(file_path, new_path)
            self.log(f"File moved to {new_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")

    def duplicate_image(self, file_path, duplicate_path):
        """
        创建图片文件的副本。
        :param file_path: 要复制的图片文件的路径。
        :param duplicate_path: 副本的路径。
        """
        if not isinstance(file_path, str) or not isinstance(duplicate_path, str):
            raise ValueError("File path and duplicate path must be strings.")

        try:
            shutil.copy(file_path, duplicate_path)
            self.log(f"File duplicated to {duplicate_path}", "INFO")
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "ERROR")
        except IOError as e:
            self.log(f"IO Error: {e}", "ERROR")






        