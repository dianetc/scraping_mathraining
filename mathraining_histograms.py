import argparse
import requests
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import defaultdict

def get_args():
    parser = argparse.ArgumentParser(description="Analyze Mathraining profile")
    parser.add_argument("-url", "--url", type=str, help="Mathraining profile URL")
    args = parser.parse_args()
    
    if not args.url:
        args.url = input("Please enter the Mathraining profile URL: ")
    
    return args

def scrape_profile(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def process_data(soup):
    categories = {
        'Combinatoire': defaultdict(int),
        'Géométrie': defaultdict(int),
        'Théorie des nombres': defaultdict(int),
        'Algèbre': defaultdict(int),
        'Équations fonctionnelles': defaultdict(int),
        'Inégalités': defaultdict(int)
    }

    resolutions_table = soup.find('table', class_='table middle_aligned my-0')
    if resolutions_table:
        rows = resolutions_table.find_all('tr')
        for row in rows:
            points_cell = row.find('td', class_='text-center fw-bold user_color')
            description_cell = row.find('td', style='')
            if points_cell and description_cell:
                points_text = points_cell.text.strip()
                description_text = description_cell.text.strip()
                if points_text.startswith('+') and 'Problème #' in description_text:
                    points = int(points_text.strip('+'))
                    category = next((cat for cat in categories.keys() if cat in description_text), None)
                    if category:
                        categories[category][points] += 1
    else:
        print("Couldn't find 'Résolutions' table.")
    return categories

def create_histograms(data):
    df = pd.DataFrame([(cat, point, count) 
                       for cat, counts in data.items() 
                       for point, count in counts.items()],
                      columns=['Category', 'Points', 'Count'])

    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"] 
    sns.set_palette(sns.color_palette(colors))

    num_categories_with_data = len(df['Category'].unique())
    num_rows = (num_categories_with_data + 1) // 2
    num_cols = 2
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(10, 8))  
    fig.subplots_adjust(hspace=0.3, wspace=0.1)


    handles = []
    labels = []
    for point, color in zip(df['Points'].unique(), colors):
        handles.append(plt.Rectangle((0, 0), 1, 1, color=color))
        labels.append(point)
    labels = sorted(labels)

    for (category, group), ax in zip(df.groupby('Category'), axs.ravel()):
        bars = sns.barplot(x='Points', y='Count', data=group, ax=ax)
        for bar in bars.patches:
            bar.set_width(0.60)  
        ax.set_title(category, fontsize=8) 
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.grid(False)
        ax.set_yticklabels([])
        for bar in bars.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2,
                    height / 2, 
                    str(int(height)),  
                    ha='center', 
                    va='center',
                    fontsize=7, 
                    fontweight='bold')
        ax.set_xticks([])

    for ax in axs.flat[num_categories_with_data:]:
        fig.delaxes(ax)

    fig.legend(handles, labels, title='Points', loc='upper center', bbox_to_anchor=(0.5, 1), ncol=len(labels), fontsize=8)
    plt.tight_layout()
    sns.despine()
    plt.show()

if __name__ == '__main__':
    args = get_args()
    soup = scrape_profile(args.url)
    data = process_data(soup)
    create_histograms(data)
