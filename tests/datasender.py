import requests
import json, re

session = requests.session()
url = "http://localhost:7071/api/http_trigger"
with open('input.json', encoding='utf-8') as json_file:
    data = json.load(json_file)
# print(data)
response = session.post(url, json=data)
print(response.status_code, response.json())

# def test2():
#     text = "mantis\n81845"
#     result = find_word_after(text, "mantis")
#     return result

# def find_word_after(input: str, match_word: str):
#     pattern = rf"{re.escape(match_word)}\n(.*)"
#     match = re.search(pattern, input)
#     return match.group(1) if match else None

# if __name__ == "__main__":
#     result = test2()
#     print(result)