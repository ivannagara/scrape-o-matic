import requests
from bs4 import BeautifulSoup
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

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
        snippet_element = item.find('span', class_='aCOpRe')

        title = title_element.text.strip() if title_element else 'No title'
        link = link_element['href'] if link_element else 'No link'
        summary = summary_element.text.strip() if summary_element else 'No summary'
        snippet = snippet_element.text if snippet_element else 'No snippet'
        
        articles.append({
            'title': title,
            'link': link,
            'summary': summary,
            'snippet': snippet
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
        print(f"Snippet: {article['snippet']}")
        print('-' * 80)
    time.sleep(random.randint(1, 5))  # Random delay to avoid being blocked

if __name__ == '__main__':
    main()