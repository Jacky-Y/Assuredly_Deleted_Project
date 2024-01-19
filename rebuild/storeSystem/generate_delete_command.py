import json
import random
import datetime

def generate_delete_commands(data_list):
    delete_commands = []

    for item in data_list:
        for info_id, types in item.items():
            command = {
                "systemID": "0x40000000",
                "systemIP": "127.0.0.1",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": {
                    "affairsID": ''.join(random.choices('0123456789', k=8)),
                    "userID": "u100000003",
                    "infoID": info_id,
                    "deleteMethod": "overwrittenDelete",
                    "deleteGranularity": "",
                    "deleteNotifyTree": "{\"b1000\": {\"children\": []}}"
                },
                "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            # 设置 deleteGranularity
            if not set(types).issubset({'Image', 'Video', 'Audio', 'Text'}):
                command['data']['deleteGranularity'] = random.choice(types)

            delete_commands.append(command)

    return delete_commands

# 示例数据
data_list = [{'36e092b55c5ee6f8': ['Text']}, {'d7fbf0a008b230eb': ['Text']}, {'eb6bc22b7c593834': ['Audio']}, {'477c3651a180c597': ['Audio']}, {'959092e0a8900e58': ['Audio']}, {'efd07cb02e009e62': ['Audio']}, {'c975c5c30a5c3d7c': ['Audio']}, {'bc147b7c3e5e5fd8': ['Audio']}, {'a064b47c032be3ae': ['Audio']}, {'f0bd5fbb0142ec32': ['Audio']}, {'1c24416e618c5ea1': ['Audio']}, {'e55ef4db1eae899f': ['Text']}, {'8e928f4cf65f76a3': ['Audio']}, {'cf31e1d994dfa62f': ['Video']}, {'3982c18ab5060996': ['Video']}, {'c203410b1968ecc5': ['Video']}, {'422e95ab9254ac3f': ['Video']}, {'654d312629213524': ['Video']}, {'ccac7398d56880df': ['Video']}, {'e872be56f8e9db12': ['Video']}, {'e5964962e9505343': ['Video']}, {'2c710dac82e4fe59': ['Video']}, {'7691763731506f1f': ['Text']}, {'7378bc0e2e05b608': ['Video']}, {'4d1d3f90950b665c': ['Image']}, {'1ad6ad62d8fbe6d2': ['Image']}, {'d879f3a4b4fbb54c': ['Image']}, {'a567c01442ef4f79': ['Image']}, {'79296ab4036063b8': ['Image']}, {'5df70b3f2c2dda48': ['Image']}, {'cfbd65d811a8ec68': ['Image']}, {'c853c42fa8f861a3': ['Image']}, {'02d891618f38fed1': ['Image']}, {'4e9f014afbdb26db': ['Text']}, {'9456f97140862b31': ['Image']}, {'32d16ecd30814b32': ['Name', 'Gender', 'Phone', 'Address', 'Age', 'Email', 'Occupation', 'Nationality', 'Hobbies', 'Education']}, {'fa2295f9ae3faa1d': ['Name', 'Gender', 'Phone', 'Address', 'Age', 'Email', 'Occupation', 'Nationality', 'Hobbies', 'Education']}, {'2704926c81bcf7bf': ['Name', 'Gender', 'Phone', 'Age', 'Nationality']}, {'49d2119f9c6849b9': ['Name', 'Gender', 'Phone', 'Email', 'Hobbies']}, {'a065ba981d8f3e50': ['Occupation']}, {'f6cc46f4e153dd1e': ['Phone', 'Nationality', 'Hobbies']}, {'5f9d0cd445c6bb59': ['Name', 'Gender', 'Phone', 'Address', 'Age', 'Email', 'Occupation', 'Nationality', 'Hobbies', 'Education']}, {'4384151fd6cb18bc': ['Address', 'Education']}, {'a24089424caec54f': ['Name', 'Gender', 'Address', 'Age', 'Education']}, {'0d0a69e08593ce0e': ['Text']}, {'f2b2edad6b63bc2f': ['Email', 'Education']}, {'c55d4a6611892b4e': ['Text']}, {'ff90f11c11ee8f2b': ['Text']}, {'8165f808651a4f5f': ['Text']}, {'774070e743408b39': ['Text']}]

# 生成删除指令
commands = generate_delete_commands(data_list)

# 将结果保存到 JSON 文件
with open('delete_commands.json', 'w', encoding='utf-8') as file:
    json.dump(commands, file, ensure_ascii=False, indent=4)
