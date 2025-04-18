import time
import json
import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Load Flipkart product URLs (previously collected)
with open("./data/urls/product_urls.json", "r", encoding="utf-8") as f:
    PRODUCT_URLS = json.load(f)

def clean_filename(name):
    name = name.replace(" ", "_")
    name = re.sub(r'[<>:"/\\|?*\xa0]', '', name)
    name = re.sub(r'[^\w\-_.]', '', name)
    return name.lower()

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def normalize_key(key):
    return re.sub(r'\W+', '_', key.strip().lower())

STANDARD_KEYS = {
    "battery_capacity": ["battery_capacity", "battery", "battery_power", "capacity"],
    "display_type": ["display_type", "screen_type"],
    "camera": ["primary_camera", "rear_camera", "camera"],
    "network_type": ["network_type", "supported_networks", "internet_connectivity"],
    "ram": ["ram"],
    "storage": ["internal_storage", "storage"],
    "processor_type": ["processor_type", "processor_brand", "processor_core"]
}

def standardize_specs(specs):
    normalized = {normalize_key(k): v for k, v in specs.items()}
    standardized = {}

    for std_key, aliases in STANDARD_KEYS.items():
        for alias in aliases:
            if alias in normalized:
                standardized[std_key] = normalized[alias]
                break
        else:
            standardized[std_key] = "Unknown"

    return standardized

def extract_reviews(driver, product_url, max_reviews=500):
    driver.get(product_url)
    time.sleep(3)

    reviews = []
    specs = {}
    product_info = {}

    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            product_info["title"] = soup.find("span", class_="VU-ZEz").text.strip()
        except AttributeError:
            print(f"Title not found for {product_url}")
            product_info["title"] = "Unknown"

        try:
            product_info["price"] = soup.find("div", class_="Nx9bqj CxhGGd").text.strip().replace("₹", "").replace(",", "")
        except AttributeError:
            print(f"Price not found for {product_url}")
            product_info["price"] = "Unknown"

        try:
            product_info["rating"] = soup.find("div", class_="XQDdHH").text.strip()
        except AttributeError:
            print(f"Rating not found for {product_url}")
            product_info["rating"] = "Unknown"

        product_info["brand"] = product_info["title"].split()[0]
        # Extract specifications
        spec_table = soup.find_all("div", class_="_1OjC5I")
        for block in spec_table:
            rows = block.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 2:
                    specs[cells[0].text.strip()] = cells[1].text.strip()

        product_info["normalized_specs"] = standardize_specs(specs)

        # Try to open all reviews
        try:
            see_all = driver.find_element(By.CSS_SELECTOR, "._23J90q.RcXBOT")
            see_all.click()
            time.sleep(2)
        except:
            pass

        while len(reviews) < max_reviews:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.find_all("div", class_="ZmyHeo")
            for review in review_blocks:
                text = review.text.replace("READ MORE", "").strip()
                reviews.append(text)
                if len(reviews) >= max_reviews:
                    break

            try:
                next_buttons = driver.find_elements(By.XPATH, "//a[contains(@class, '_9QVEpD')]")
                for btn in next_buttons:
                    if btn.text.strip().lower() == "next":
                        btn.click()
                        time.sleep(2)
                        break
                else:
                    break
            except:
                break

    except Exception as e:
        print(f"❌ Error scraping {product_url}: {e}")

    return {
        "metadata": product_info,
        "reviews": reviews[:max_reviews]
    }

def main():
    driver = init_driver()
    os.makedirs("data/raw", exist_ok=True)
    all_products = []

    for url in PRODUCT_URLS:
        print(f"🔍 Scraping: {url}")
        data = extract_reviews(driver, url)
        all_products.append(data)

        name = clean_filename(data["metadata"]["title"])
        with open(f"data/raw/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    driver.quit()
    print("✅ Scraping completed and saved in data/raw/")

if __name__ == "__main__":
    main()
