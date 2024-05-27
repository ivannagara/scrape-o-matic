import requests
from bs4 import BeautifulSoup
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless Chrome
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def google_search(driver, query):
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # Allow time for results to load

    links = driver.find_elements(By.XPATH, '//div[@class="tF2Cxc"]//a')
    urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
    print(f"Found URLs: {urls}")  # Debug: Print found URLs
    return urls

def fetch_page_content(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def is_landing_page(soup):
    # Check for multiple article links
    article_links = soup.find_all('a', href=True)
    if len(article_links) > 10:
        return True

    # Check for article containers
    article_containers = soup.find_all(['div', 'article'], class_=['article', 'card', 'post', 'news-item'])
    if len(article_containers) > 5:
        return True

    # Check for pagination
    pagination = soup.find_all(['nav', 'div'], class_=['pagination', 'pager'])
    if pagination:
        return True

    return False

def parse_article_page(html_content, url):
    if not html_content:
        print(f"No content for URL: {url}")  # Debug: Print if no content is fetched
        return {
            'URL': url,
            'Title': 'N/A',
            'Description': 'N/A',
            'Paragraphs': 'N/A',
            'Date': 'N/A',
            'Author': 'N/A',
            'Publisher': 'N/A',
            'Keywords': 'N/A',
            'Image': 'N/A',
            'Tags': 'N/A'
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.find('title').text if soup.find('title') else 'N/A'
    description_tag = soup.find('meta', attrs={"name": "description"})
    description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else 'N/A'
    paragraphs = ' '.join([p.text for p in soup.find_all('p')])
    date_tag = soup.find('meta', attrs={"property": "article:published_time"})
    date = date_tag['content'] if date_tag and 'content' in date_tag.attrs else 'N/A'
    author_tag = soup.find('meta', attrs={"name": "author"})
    author = author_tag['content'] if author_tag and 'content' in author_tag.attrs else 'N/A'
    publisher_tag = soup.find('meta', attrs={"name": "publisher"})
    publisher = publisher_tag['content'] if publisher_tag and 'content' in publisher_tag.attrs else 'N/A'
    keywords_tag = soup.find('meta', attrs={"name": "keywords"})
    keywords = keywords_tag['content'] if keywords_tag and 'content' in keywords_tag.attrs else 'N/A'
    image_tag = soup.find('meta', attrs={"property": "og:image"})
    image = image_tag['content'] if image_tag and 'content' in image_tag.attrs else 'N/A'
    tags = ', '.join([tag['content'] for tag in soup.find_all('meta', attrs={"property": "article:tag"})])
    
    return {
        'URL': url,
        'Title': title,
        'Description': description,
        'Paragraphs': paragraphs,
        'Date': date,
        'Author': author,
        'Publisher': publisher,
        'Keywords': keywords,
        'Image': image,
        'Tags': tags
    }

def parse_landing_page(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    for article in soup.find_all('article'):
        link = article.find('a', href=True)
        if link:
            article_url = link['href']
            if not article_url.startswith('http'):
                article_url = base_url + article_url
            articles.append(article_url)
    return articles

def scrape_news_articles(urls, headers):
    results = []
    for url in urls:
        html_content = fetch_page_content(url, headers)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check if the page is a landing page
        if is_landing_page(soup):
            article_urls = parse_landing_page(html_content, base_url=url)
            for article_url in article_urls:
                article_content = fetch_page_content(article_url, headers)
                info = parse_article_page(article_content, article_url)
                print(f"Scraped data for {article_url}: {info}")  # Debug: Print scraped data
                results.append(info)
        else:
            # Assume article page for other URLs
            info = parse_article_page(html_content, url)
            print(f"Scraped data for {url}: {info}")  # Debug: Print scraped data
            results.append(info)
        time.sleep(1)  # Sleep to avoid overwhelming the server
    return results

def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

if __name__ == "__main__":
    query = "berita pelanggaran ham"  # Replace with your search query
    driver = setup_driver()
    news_urls = google_search(driver, query)
    driver.quit()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    results = scrape_news_articles(news_urls, headers)
    save_to_csv(results, 'news_data.csv')
