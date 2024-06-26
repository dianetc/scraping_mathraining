from os.path import join as pjoin
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def generate_mathtraining_urls(country_id, num_pages):
    base_url = "https://www.mathraining.be/users"
    urls = []

    for page in range(1, num_pages + 1):
        url = f"{base_url}?country={country_id}&page={page}&title=0"
        urls.append(url)

    return urls

def extract_profiles_from_urls(urls):
    profiles = []  # Initialize a list to store all profiles

    for url in urls:
        # Use requests to retrieve the content of the webpage
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'users_table'})  # Find the table with users

            # Skip if table is not found
            if not table:
                continue

            # Iterate through each row in the table (skip the header row)
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')  # Find all the 'td' tags
                if len(cells) > 1:
                    name = cells[1].get_text(strip=True)  # Extract the name
                    link = cells[1].find('a')['href']  # Extract the link
                    # Append the name and link to the profiles list
                    profiles.append({'name': name, 'link': f"https://www.mathraining.be{link}"})
        else:
            print(f"Failed to retrieve {url}. Status code:", response.status_code)

    return profiles
def convert_french_date(french_date):
    # Define a dictionary to map French month names to numbers
    month_mapping = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }

    # Split the French date into components
    day, month_name, year = french_date.split()

    # Map the French month name to a number
    month = month_mapping[month_name.lower()]

    # Create a datetime object from the day, month, and year
    date_obj = datetime(year=int(year), month=month, day=int(day))

    # Format the date as MM/DD/YYYY
    return date_obj.strftime('%m/%d/%Y')


def scrape_profile_details(profile):
    url = profile['link']
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        user_name = soup.find_all("span", class_="fw-bold")[0].text.strip()
        score = soup.find(string="Score").find_next("td", class_="myvalue").text.strip()
        exercises_completed = soup.find(string="Exercices").find_next("div", class_="progress_nb").text.strip()
        problems_solved = soup.find(string="Problèmes").find_next("div", class_="progress_nb").text.strip()

        evolution_div = soup.find("div", class_="g-col-12 basic_container p-1")
        sign_up_date = None
        if evolution_div:
            date_span = evolution_div.find("span", class_="user_color")
            if date_span:
                french_date = date_span.text.strip()
                sign_up_date = convert_french_date(french_date)

        return {
            'Name': user_name,
            'Link': url,
            'Score': score,
            'Exercises Completed': exercises_completed,
            'Problems Solved': problems_solved,
            'Sign Up Date': sign_up_date
        }
    else:
        print(f"Failed to retrieve {url}. Status code:", response.status_code)
        return None

def create_profiles_dataframe(profiles):
    data = []
    for profile in profiles:
        profile_data = scrape_profile_details(profile)
        if profile_data:
            data.append(profile_data)
    return pd.DataFrame(data)

if __name__ == '__main__':
    ivory_coast_country_id = 48
    num_pages = 3
    Ivory_Coast_URLs = generate_mathtraining_urls(ivory_coast_country_id,num_pages)
    profiles = extract_profiles_from_urls(Ivory_Coast_URLs)
    df = create_profiles_dataframe(profiles)

    current_date = datetime.datetime.now().strftime("%m_%d_%Y")
    filename = f'ivory_coast_mathtraining_snapshot_{current_date}.csv'
    df.to_csv(filename)
