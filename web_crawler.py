import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random

def init_driver():
    # Initialize the web driver (make sure to specify the correct path to your web driver)
    driver = webdriver.Chrome()
    return driver

def search_query(driver, query):
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

def extract_results(driver):
    time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
    extracted_data = []

    for result in results:
        try:
            title_element = result.find_element(By.TAG_NAME, 'h3')
            link_element = result.find_element(By.TAG_NAME, 'a')
            snippet_element = result.find_element(By.CSS_SELECTOR, 'div.IsZvec')

            title = title_element.text if title_element else 'No title'
            link = link_element.get_attribute('href') if link_element else 'No link'
            snippet = snippet_element.text if snippet_element else 'No snippet'

            extracted_data.append({
                'title': title,
                'link': link,
                'snippet': snippet
            })
        except Exception as e:
            print(f"Error extracting result: {e}")
    return extracted_data

def visit_links_and_extract(driver, links, page_load_timeout=10):
    detailed_data = []

    for link in links:
        try:
            print(f"Visiting {link}")
            driver.set_page_load_timeout(page_load_timeout)
            driver.get(link)
            time.sleep(random.uniform(2, 4))  # Random delay to avoid detection

            try:
                # Wait for the first paragraph to load or until the timeout is reached
                WebDriverWait(driver, page_load_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'p'))
                )
                paragraph = driver.find_element(By.TAG_NAME, 'p').text
                print(paragraph)
                detailed_data.append({
                    'link': link,
                    'content': paragraph
                })
                print('-' * 80)
            except TimeoutException:
                print(f"Timeout waiting for elements in {link}")
        except TimeoutException:
            print(f"Timeout loading {link}")
        except Exception as e:
            print(f"Error visiting {link}: {e}")

    return detailed_data

def save_to_csv(data, filename='output.csv'):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    logging.info("Starting web scraper")
    driver = init_driver()
    query = "berita pelanggaran ham"
    search_query(driver, query)
    results = extract_results(driver)

    # Collect links from search results
    links = [result['link'] for result in results if result['link']]

    # Visit each link and extract detailed information
    detailed_data = visit_links_and_extract(driver, links, page_load_timeout=10)
    driver.quit()
    
    if detailed_data:
        save_to_csv(detailed_data, filename='scraped_data.csv')

    for data in detailed_data:
        print(f"Link: {data['link']}")
        print(f"Content: {data['content']}")
        print('-' * 80)

if __name__ == '__main__':
    main()