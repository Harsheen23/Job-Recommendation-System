import requests

API_KEY = "AIzaSyAFpak-rI5YOhIRaZnk7JfB8ib4ruIqxDM"
query = "Python programming course"
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=playlist&q={query}&key={API_KEY}"

response = requests.get(url)
data = response.json()

for item in data.get("items", []):
    print(item["snippet"]["title"], item["id"]["playlistId"])
