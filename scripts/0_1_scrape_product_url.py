import os
import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def init_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def scrape_product_urls(query="smartphones", max_products=50):
    os.makedirs("data/urls", exist_ok=True)
    driver = init_driver()

    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.flipkart.com/search?q={encoded_query}"
    driver.get(search_url)
    time.sleep(3)

    product_urls = set()
    last_count = 0
    page_count = 0
    max_pages = 10

    while len(product_urls) < max_products and page_count < max_pages:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = soup.select('a[href*="/p/"]')
        for link in links:
            href = link.get("href")
            if href and "/p/" in href:
                full_url = "https://www.flipkart.com" + href.split("?")[0]
                product_urls.add(full_url)
                if len(product_urls) >= max_products:
                    break

        print(f"🔗 Collected {len(product_urls)} product URLs so far...")

        if len(product_urls) == last_count:
            print("⚠️ No new URLs found. Stopping.")
            break

        last_count = len(product_urls)
        page_count += 1

        try:
            next_btn = driver.find_element(By.XPATH, '//a[contains(@class, "_9QVEpD")]')
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
        except:
            print("❌ No 'Next' button found or pagination ended.")
            break

    driver.quit()

    url_list = list(product_urls)
    with open("data/urls/product_urls.json", "w", encoding="utf-8") as f:
        json.dump(url_list, f, indent=2)

    print(f"✅ Saved {len(url_list)} product URLs to data/urls/product_urls.json")

if __name__ == "__main__":
    scrape_product_urls()
