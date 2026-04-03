import requests
from streamlit import header
from werkzeug.user_agent import UserAgent

url = "https://www.nykaa.com/skin/moisturizers/face-moisturizer-day-cream/c/8394"

headers = {"User-Agent" : "Mozilla/5.0"}

response = requests.get(url, headers=headers)

print (response.status_code)
