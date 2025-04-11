from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

url = "https://www.oregonlegislature.gov/bills_laws/ors/ors350.html"

raw = requests.get(url)

soup = bs(raw.text,'html.parser')

soup.find_all("p")

time_seen = 0
passed = False
out_list = []

for par in soup.find_all('p')[310:]:

    if par.text == """POLICY ON HIGHER 
    EDUCATION""":
        time_seen += 1
    if time_seen == 1:
        passed = True
    if passed == True:
        out_list.append(par.text)

Policies_raw = soup.find_all('p')[314:]

policy_list = []
current_policy = []

for pol in Policies_raw:
    if pol.text.strip().startswith("350."):
        if current_policy:
            policy_list.append(" ".join(current_policy))
        current_policy = [pol.text.strip()]
    else:
        current_policy.append(pol.text.strip())

# Add the last policy to the list
if current_policy:
    policy_list.append(" ".join(current_policy))

import Law_Agent
Law_Agent.process_policy_deadlines(policy_list, '/home/user/DataspellProjects/OregonLegislature')
