import asyncio
from playwright.async_api import async_playwright
import requests
import json
import os
from amazon import get_product as get_amazon_product



def post_results(results, endpoint, search_text, source):
    headers = {
        "Content-Type": "application/json"
    }
    data = {"data": results, "search_text": search_text, "source": source}

    print("Sending request to", endpoint)
    response = post("http://localhost:5000" + endpoint,
                    headers=headers, json=data)
    print("Status code:", response.status_code)

async def main(url, search_text, response_route):
    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return
    
    async with async_playwrite() as pw:
        print('Connecting to browser...')
        browser = await pw.chromium.connect_over_cdp(browser_ur)
        page = await browser.new_page()
        print("Connected")
        await page.goto(url, timeout=120000)
        print("Loaded initial page.")
        aearch_page = await search(metadata, page,search_text)

        def fun(x): return None
        if url == AMAZON:
            func = get_amazon_product
        else:
            raise Exception("Invalid URL")
        
        results = await get_products(search_page, search_text, metadata["product_selector"], func)
        print("Saving results.")
        post_results(results, response_route, search_text, url)

        await browser.close()

if __name__ == "__main__":
    # test script
    asyncio.run(main(AMAZON, "ryzen 9 3950x", response_route))