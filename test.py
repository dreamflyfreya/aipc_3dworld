import requests

url = 'http://localhost:5000/chat'
data = {'message': 'Why is the sky blue?'}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)