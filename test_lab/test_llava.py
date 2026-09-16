import requests
import base64

# 1. Read the image and convert it to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "sample.jpg"
image_b64 = encode_image(image_path)

# 2. Set up the request to your local Ollama API
url = "http://localhost:11434/api/generate"
payload = {
    "model": "llava",
    "prompt": "What is happening in this image? Keep it to one sentence.",
    "images": [image_b64],
    "stream": False
}

# 3. Send it and print the result
print("Sending image to LLaVA... wait")
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("\nLLaVA says:")
    print(response.json()['response'])
else:
    print(f"\nError! Status code: {response.status_code}")
    print(response.text)