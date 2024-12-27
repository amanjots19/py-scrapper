
# Web Scrapper

This project implements a FastAPI-based web scraping tool using BeautifulSoup to scrape product data from an E-commerce website. The tool extracts the product title, price, and image URL, and saves the scraped data in a JSON format.

## Prerequisites

- Python 3.7+
- Required Python packages: FastAPI, Requests, BeautifulSoup, Pydantic, uvicorn

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/amanjots19/py-scrapper.git
   ```
2. Install the dependencies
``` bash
pip install -r requirements.txt
```
## API Usage

### Endpoint: `/scrape`

This endpoint allows you to start the scraping process. You can customize the settings (like the number of pages to scrape) through the request body.

### Method: `POST`

### Request Body:

```json
{
  "max_pages": 10
}
```
## Query Parameter:
- `token`: Your authentication token (required).

## Response:

```json
{
  "message": "Scraped 10 products",
  "data": [
    {
      "product_title": "3m Espe Sof-Lex Finishing Strips",
      "product_price": 2272.00,
      "image_ref": "https://dentalstall.com/wp-content/uploads/2023/03/3m_espe_sof-lex_finishing_strips_-_refill-300x300.jpg"
    },
  ]
}
```

## Example:

### Bash:

```bash
curl -X 'POST' \
  'http://localhost:8000/scrape?token=$token' \
  -H 'Content-Type: application/json' \
  -d '{
    "max_pages": 5
  }'
```
## Running the API

To run the FastAPI application:

 ### Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
  
## File Structure

- **`main.py`**: The FastAPI application and the core scraping logic.
- **`scraped_data.json`**: JSON file where scraped data is saved.
- **`images/`**: Directory where product images are stored.

---

## Image Downloading

- Images are downloaded and stored in the **`images/`** directory.
- The scraper extracts valid image URLs from the `img` tags inside the `.mf-product-thumbnail` div.
- If an image URL is invalid or missing, the product is skipped.

---

## Cache

To optimize performance, the scraper uses a caching mechanism:
- Products with the same title and price that have already been scraped are skipped.

---

## Saving Data

- Scraped product data is saved in a JSON file named **`scraped_data.json`**.
- The JSON file contains a list of products, each with:
  - `product_title`
  - `product_price`
  - `image_ref` (URL of the product image in Local Directory)

---


  

