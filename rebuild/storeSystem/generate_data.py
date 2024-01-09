import json
import random
import os

# 预设列表
presets = {
    "Name": ["John Doe", "Jane Smith", "Alice Johnson", "Bob Brown"],
    "Gender": ["Male", "Female", "Non-Binary"],
    "Phone": ["123-456-7890", "987-654-3210", "555-444-3333"],
    "Address": ["123 Main St, City, Country", "456 Elm St, AnotherCity, AnotherCountry", "789 Maple St, YetAnotherCity, YetAnotherCountry"],
    "Age": ["25", "30", "35", "40"],
    "Email": ["john.doe@example.com", "jane.smith@example.com", "alice.johnson@example.com"],
    "Occupation": ["Engineer", "Doctor", "Artist", "Lawyer"],
    "Nationality": ["American", "British", "Chinese", "Indian"],
    "Hobbies": ["Reading", "Swimming", "Traveling", "Cooking"],
    "Education": ["PhD", "Masters", "Bachelors", "High School"]
}

def generate_json_files(start, end):
    """
    Generate JSON files with names from start.json to end.json.
    Each file contains randomly selected keys from presets with non-empty values.
    """
    for i in range(start, end + 1):
        # Randomly select some keys
        selected_keys = random.sample(presets.keys(), random.randint(1, len(presets)))
        data = {key: random.choice(presets[key]) if key in selected_keys else None for key in presets}

        # Create and write to the JSON file
        file_name = f'./testdata/{i}.json'
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)

    return f"Generated JSON files from {start}.json to {end}.json"

def generate_image_files(start, end):
    """
    Generate image files with extensions jpg, jpeg, png, gif, bmp.
    Each file contains randomly generated binary content.
    The files are named from start to end with each extension.
    """
    extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

    for i in range(start, end + 1):
        ext = random.choice(extensions)
        file_name = f'./testdata/{i}.{ext}'
        content = b'\x00' * 1024  # Binary content for images
        with open(file_name, 'wb') as file:
            file.write(content)

    return f"Generated image files from {start} to {end} with extensions {extensions}"

def generate_video_files(start, end):
    """
    Generate video files with extensions mp4, avi, mov, wmv.
    Each file contains randomly generated binary content.
    The files are named from start to end with each extension.
    """
    extensions = ['mp4', 'avi', 'mov', 'wmv']

    for i in range(start, end + 1):
        ext = random.choice(extensions)
        file_name = f'./testdata/{i}.{ext}'
        content = b'\x00' * 1024  # Binary content for video files
        with open(file_name, 'wb') as file:
            file.write(content)

    return f"Generated video files from {start} to {end} with extensions {extensions}"

def generate_audio_files(start, end):
    """
    Generate audio files with extensions mp3, wav, aac, flac.
    Each file contains randomly generated binary content.
    The files are named from start to end with each extension.
    """
    extensions = ['mp3', 'wav', 'aac', 'flac']
    for i in range(start, end + 1):
        ext = random.choice(extensions)
        file_name = f'./testdata/{i}.{ext}'
        content = b'\x00' * 1024  # Binary content for audio files
        with open(file_name, 'wb') as file:
            file.write(content)

    return f"Generated audio files from {start} to {end} with extensions {extensions}"


def generate_text_files(start, end):
    """
    Generate text files with the extension txt.
    Each file contains randomly generated text content.
    The files are named from start to end with the txt extension.
    """
    for i in range(start, end + 1):
        file_name = f'./testdata/{i}.txt'
        content = "This is a text file with some random content.\n" * 10  # Text content for text files
        with open(file_name, 'w') as file:
            file.write(content)

    return f"Generated text files from {start}.txt to {end}.txt"

# Example usage
# generate_text_files(1, 10) # This will generate text files named 1.txt to 10.txt


# Example usage
# generate_video_files(1, 10) # This will generate video files named 1.mp4, 1.avi, etc. to 10.mp4, 10.avi, etc.
# generate_audio_files(1, 10) # This will generate audio files named 1.mp3, 1.wav, etc. to 10.mp3, 10.wav, etc.



# Example usage
# generate_image_files(1, 


# Generate JSON files named from 1.json to 100.json
generate_text_files(1, 10)
generate_audio_files(11, 20)
generate_video_files(21, 30)
generate_image_files(31,40) 
generate_json_files(41, 50)
