import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
# import Law_Agent
import re

def fetch_page_content(url):
    """
    Fetch the HTML content of a given URL.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    return response.text

def parse_policies(html_content):
    """
    Parse the HTML content to extract policies.
    """
    soup = bs(html_content, 'html.parser')
    paragraphs = soup.find_all('p')

    # Extract policies
    policies_raw = paragraphs[314:]
    policy_list = []
    current_policy = []

    for paragraph in policies_raw:
        text = paragraph.text.strip()
        if text.startswith("350."):
            if current_policy:
                policy_list.append(" ".join(current_policy))
            current_policy = [text]
        else:
            current_policy.append(text)

    # Add the last policy to the list
    if current_policy:
        policy_list.append(" ".join(current_policy))

    return policy_list

def get_policy_deadlines(policy_list, pattern):
    """
    Process policies and save deadlines to a CSV file.
    """
    regex = re.compile(pattern, re.IGNORECASE)
    return [match.group(1) for item in policy_list if (match := regex.search(item))]

def main():
    """
    Main function to orchestrate the scraping and processing of policies.
    """
    url = "https://www.oregonlegislature.gov/bills_laws/ors/ors350.html"
    output_path = '/home/user/DataspellProjects/OregonLegislature/policy_deadlines.csv'

    # Fetch and parse policies
    html_content = fetch_page_content(url)
    policy_list = parse_policies(html_content)

    # Process policy deadlines
    result = get_policy_deadlines(policy_list, r"\b(?:no later than|on or before)\s(.*)")
    print(result)
    print(len(result))
    
if __name__ == '__main__':
    main()