import requests
from bs4 import BeautifulSoup
import time
import random

def get_html(url):
    response = requests.get(url)
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def extract_data(soup):
    # Example extraction for news articles
    articles = []
    for item in soup.find_all('article'):
        title_element = item.find('h2')
        link_element = item.find('a')
        summary_element = item.find('p')

        title = title_element.text.strip() if title_element else 'No title'
        link = link_element['href'] if link_element else 'No link'
        summary = summary_element.text.strip() if summary_element else 'No summary'

        articles.append({
            'title': title,
            'link': link,
            'summary': summary
        })
    return articles
    
def main():
    url = 'https://www.cnbcindonesia.com'
    html = get_html(url)
    print(html)  # Print the raw HTML to inspect
    soup = parse_html(html)
    articles = extract_data(soup)
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Summary: {article['summary']}")
        print('-' * 80)
    time.sleep(random.randint(1, 5))  # Random delay to avoid being blocked

if __name__ == '__main__':
    main()