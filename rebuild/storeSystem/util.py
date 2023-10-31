import json

def overwrite_file(target_files, granularity, alg_param, level):
    """
    模拟覆写文件函数
    :param target_files: 要覆写的目标文件列表
    :param granularity: 覆写的粒度（特定字段名）
    :param alg_param: 用于覆写的随机数
    :param level: 覆写的次数
    """
    for _ in range(level):
        for file_path in target_files:
            try:
                # 读取 JSON 文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 根据 granularity 覆写特定字段或整个文件
                if granularity:
                    if granularity in data:  # 检查字段是否存在
                        data[granularity] = alg_param  # 覆写该字段
                    else:
                        print(f"Field '{granularity}' not found in {file_path}.")
                        continue  # 如果字段不存在，跳过此次覆写并处理下一个文件

                else:
                    # 如果没有指定 granularity，直接将文件内容覆写为 alg_param
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(alg_param)
                        continue  # 跳过下面的 JSON 写入步骤，直接处理下一个文件

                # 保存修改后的 JSON 数据
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error processing file {file_path}: {e}")

overwrite_file(["./storeSystem/test/0c1d2e3f4g5h.json"], "", "sdsdfadgagaga", 1)