from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

def load_config():
    # 构建 config.json 文件的路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'deleteSystem', 'config.json')

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get('classifySystem', {})
    except FileNotFoundError:
        print("配置文件未找到。请确保 config.json 文件在正确的位置。")
        return {}
    except json.JSONDecodeError:
        print("配置文件格式错误。请确保它是有效的 JSON 格式。")
        return {}
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")
        return {}

@app.route('/query', methods=['POST'])
def query_info():
    # 从请求中获取 InfoTypes 列表
    data = request.get_json()
    info_types = data.get('InfoTypes', None)

    # 如果 InfoTypes 不存在或为空列表，返回错误
    if not info_types or not isinstance(info_types, list):
        return jsonify({"error": "InfoTypes not provided or invalid"}), 400

    # # 在 info_classify.json 中查找这些 InfoTypes 的 InfoLevel
    # with open('info_classify.json', 'r') as file:
    #     info_classify_data = json.load(file)

    info_classify_data=[
    {
        "InfoType": "Name",
        "InfoLevel": 5
    },
    {
        "InfoType": "Gender",
        "InfoLevel": 3
    },
    {
        "InfoType": "Age",
        "InfoLevel": 4
    },
    {
        "InfoType": "Address",
        "InfoLevel": 5
    },
    {
        "InfoType": "Phone",
        "InfoLevel": 3
    },
    {
        "InfoType": "Email",
        "InfoLevel": 4
    },
    {
        "InfoType": "Occupation",
        "InfoLevel": 2
    },
    {
        "InfoType": "Nationality",
        "InfoLevel": 3
    },
    {
        "InfoType": "Education",
        "InfoLevel": 4
    },
    {
        "InfoType": "Hobbies",
        "InfoLevel": 1
    },
    {
        "InfoType": "Academic Records",
        "InfoLevel": 4
    },
    {
        "InfoType": "Professional Licenses",
        "InfoLevel": 4
    },
    {
        "InfoType": "Vehicle License Plate",
        "InfoLevel": 3
    },
    {
        "InfoType": "Artistic Preferences",
        "InfoLevel": 1
    },
    {
        "InfoType": "Reading Habits",
        "InfoLevel": 1
    },
    {
        "InfoType": "Gaming Habits",
        "InfoLevel": 1
    },
    {
        "InfoType": "Vacation Preferences",
        "InfoLevel": 2
    },
    {
        "InfoType": "Past Employers",
        "InfoLevel": 4
    },
    {
        "InfoType": "Credit Card Numbers",
        "InfoLevel": 5
    },
    {
        "InfoType": "Bank Account Details",
        "InfoLevel": 5
    },
    {
        "InfoType": "Investment Accounts",
        "InfoLevel": 5
    },
    {
        "InfoType": "Retirement Plans",
        "InfoLevel": 5
    },
    {
        "InfoType": "Mortgage Information",
        "InfoLevel": 5
    },
    {
        "InfoType": "Charity Work",
        "InfoLevel": 2
    },
    {
        "InfoType": "Religious Affiliations",
        "InfoLevel": 4
    },
    {
        "InfoType": "Philosophical Beliefs",
        "InfoLevel": 3
    },
    {
        "InfoType": "Personal Goals",
        "InfoLevel": 1
    },
    {
        "InfoType": "Life Achievements",
        "InfoLevel": 2
    },
    {
        "InfoType": "Personal Challenges",
        "InfoLevel": 2
    },
    {
        "InfoType": "Security Questions and Answers",
        "InfoLevel": 5
    },
    {
        "InfoType": "Frequent Flyer Number",
        "InfoLevel": 3
    },
    {
        "InfoType": "Library Card Number",
        "InfoLevel": 2
    },
    {
        "InfoType": "Gym Membership Details",
        "InfoLevel": 2
    },
    {
        "InfoType": "Subscription Services",
        "InfoLevel": 2
    },
    {
        "InfoType": "Online Shopping Preferences",
        "InfoLevel": 2
    },
    {
        "InfoType": "Favorite Entertainment",
        "InfoLevel": 1
    },
    {
        "InfoType": "Favorite Foods",
        "InfoLevel": 1
    },
    {
        "InfoType": "Preferred Brands",
        "InfoLevel": 1
    },
    {
        "InfoType": "Allergies",
        "InfoLevel": 4
    },
    {
        "InfoType": "Diseases",
        "InfoLevel": 5
    },
    {
        "InfoType": "Surgical History",
        "InfoLevel": 5
    },
    {
        "InfoType": "Blood Type",
        "InfoLevel": 3
    },
    {
        "InfoType": "Biometric Data",
        "InfoLevel": 5
    },
    {
        "InfoType": "Exercise Habits",
        "InfoLevel": 2
    },
    {
        "InfoType": "Dietary Restrictions",
        "InfoLevel": 3
    },
    {
        "InfoType": "Sleep Patterns",
        "InfoLevel": 2
    },
    {
        "InfoType": "Psychological Profile",
        "InfoLevel": 5
    },
    {
        "InfoType": "Therapy Sessions",
        "InfoLevel": 5
    },
    {
        "InfoType": "Family Medical History",
        "InfoLevel": 5
    },
    {
        "InfoType": "Genetic Information",
        "InfoLevel": 5
    },
    {
        "InfoType": "Legal Records",
        "InfoLevel": 5
    },
    {
        "InfoType": "Voting Records",
        "InfoLevel": 4
    },
    {
        "InfoType": "Charitable Donations",
        "InfoLevel": 3
    },
    {
        "InfoType": "Pet Ownership",
        "InfoLevel": 2
    },
    {
        "InfoType": "Vehicle Usage Patterns",
        "InfoLevel": 3
    },
    {
        "InfoType": "Home Ownership Details",
        "InfoLevel": 4
    },
    {
        "InfoType": "Utility Usage",
        "InfoLevel": 3
    },
    {
        "InfoType": "Travel Itineraries",
        "InfoLevel": 3
    },
    {
        "InfoType": "Digital Footprint",
        "InfoLevel": 4
    },
    {
        "InfoType": "Online Behavior",
        "InfoLevel": 4
    },
    {
        "InfoType": "Religion",
        "InfoLevel": 4
    },
    {
        "InfoType": "Political Views",
        "InfoLevel": 4
    },
    {
        "InfoType": "Income Level",
        "InfoLevel": 5
    },
    {
        "InfoType": "Net Worth",
        "InfoLevel": 5
    },
    {
        "InfoType": "Investment Details",
        "InfoLevel": 5
    },
    {
        "InfoType": "Membership in Organizations",
        "InfoLevel": 3
    },
    {
        "InfoType": "Vehicle Registration",
        "InfoLevel": 4
    },
    {
        "InfoType": "Property Ownership",
        "InfoLevel": 4
    },
    {
        "InfoType": "Loan History",
        "InfoLevel": 5
    },
    {
        "InfoType": "Insurance Policies",
        "InfoLevel": 4
    },
    {
        "InfoType": "Driver's License Number",
        "InfoLevel": 5
    },
    {
        "InfoType": "Passport Number",
        "InfoLevel": 5
    },
    {
        "InfoType": "Tax ID",
        "InfoLevel": 5
    },
    {
        "InfoType": "Credit Score",
        "InfoLevel": 5
    },
    {
        "InfoType": "Medical Record",
        "InfoLevel": 5
    },
    {
        "InfoType": "Employment History",
        "InfoLevel": 4
    },
    {
        "InfoType": "Criminal Record",
        "InfoLevel": 5
    },
    {
        "InfoType": "Travel History",
        "InfoLevel": 3
    },
    {
        "InfoType": "Fingerprint",
        "InfoLevel": 5
    },
    {
        "InfoType": "DNA Profile",
        "InfoLevel": 5
    },
    {
        "InfoType": "Marital Status",
        "InfoLevel": 3
    },
    {
        "InfoType": "Date of Birth",
        "InfoLevel": 4
    },
    {
        "InfoType": "Place of Birth",
        "InfoLevel": 4
    },
    {
        "InfoType": "Languages Spoken",
        "InfoLevel": 2
    },
    {
        "InfoType": "Emergency Contact",
        "InfoLevel": 5
    },
    {
        "InfoType": "Health Conditions",
        "InfoLevel": 5
    },
    {
        "InfoType": "Dietary Preferences",
        "InfoLevel": 1
    },
    {
        "InfoType": "Professional Skills",
        "InfoLevel": 3
    },
    {
        "InfoType": "Biography",
        "InfoLevel": 2
    },
    {
        "InfoType": "Social Media Profiles",
        "InfoLevel": 2
    }

]

    result = []
    for info_type in info_types:
        matched_item = next((item for item in info_classify_data if item["InfoType"] == info_type), None)
        if matched_item:
            result.append({"InfoType": info_type, "InfoLevel": matched_item["InfoLevel"]})
        else:
            result.append({"InfoType": info_type, "InfoLevel": "Not found"})

    return jsonify(result)

if __name__ == '__main__':
    config = load_config()
    classify_system_ip = config.get('ip', '127.0.0.1')  # 默认 IP
    classify_system_port = config.get('port', 6000)     # 默认端口

    app.run(host=classify_system_ip, port=classify_system_port)
