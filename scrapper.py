from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from bs4 import BeautifulSoup
from typing import Optional, List
from time import sleep
from hashlib import sha256
from datetime import datetime
import requests
import os
import json
import shutil

base_url = "https://dentalstall.com/shop/page/{}/"
cache = {}
app = FastAPI()

# Constants
AUTH_TOKEN = "1j3ei2or4n3905453n3t5ioj3t5i"
CACHE_EXPIRATION = 300  # in seconds

class ScrappingSettings(BaseModel):
    max_pages: Optional[int] = None

class Product(BaseModel):
    product_title: str
    product_price: float
    image_ref: str

def download_image(url: str, save_path: str):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def authenticate(token: str = Query(..., description="Authentication token")):
    print(token)
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

def cache_key(url: str):
    return sha256(url.encode()).hexdigest()

def save_to_json(data: List[Product], file_path: str):
    with open(file_path, 'w') as f:
        json.dump([item.dict() for item in data], f, indent=4)

class Scrapper:
    def __init__(self, settings: ScrappingSettings):
        self.settings = settings
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.retry_delay = 5

    def fetch_page(self, url):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt < retry_attempts - 1:
                    sleep(self.retry_delay)
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to fetch page: {e}")

    def extract_products(self, page_html: str):
        soup = BeautifulSoup(page_html, 'html.parser')
        products = []
        for item in soup.select(".product-inner"):
            try:
                product_title = item.select_one(".mf-product-content").get_text(strip=True)
                price_text = item.select_one(".price").get_text(strip=True)
                price_text = price_text.split(".")[0]

                # Remove currency symbols and convert to float
                product_price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
                thumbnail = item.select_one(".mf-product-thumbnail")
                
                image_ref = thumbnail.select_one("img")
                image_ref = image_ref.get("data-lazy-src")

                if not image_ref or not image_ref.startswith("http"):
                    print(f"Skipping product {product_title} due to invalid image URL: {image_ref}")
                    continue

                products.append(Product(
                    product_title=product_title,
                    product_price=product_price,
                    image_ref=image_ref
                ))
            except (AttributeError, ValueError) as e:
                print(f"Error processing product: {e}")
                continue
        return products

    def scrape(self):
        scrapedData = []
        for page in range(1, (self.settings.max_pages or 10) + 1):
            url = base_url.format(page)
            page_html = self.fetch_page(url)
            products = self.extract_products(page_html)

            for product in products:
                key = cache_key(product.product_title + str(product.product_price))
                if key in cache and cache[key]['price'] == product.product_price:
                    continue
                
                try:
                    save_path = f"images/{product.product_title.replace(' ', '_')[:50]}.jpg"
                    os.makedirs("images", exist_ok=True)
                    download_image(product.image_ref, save_path)
                    
                    scrapedData.append(product)
                    cache[key] = {"price": product.product_price, "timestamp": datetime.now()}
                except Exception as e:
                    print(f"Error downloading image for {product.product_title}: {e}")
                    continue
                
        return scrapedData

@app.post("/scrape")
def scrape(settings: ScrappingSettings, token: str = Query(..., description="Authentication token")):
    print(token)
    authenticate(token)
    scraper = Scrapper(settings)
    scraped_data = scraper.scrape()
    save_to_json(scraped_data, "scraped_data.json")
    print(f"Scraped {len(scraped_data)} products")
    return {"message": f"Scraped {len(scraped_data)} products", "data": scraped_data}