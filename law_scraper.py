from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

url = "https://www.oregonlegislature.gov/bills_laws/ors/ors350.html"

raw = requests.get(url)
print(raw.status_code)

soup = bs(raw.text,'html.parser')
print(soup.find_all("p"))