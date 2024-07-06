import re
import requests
from bs4 import BeautifulSoup as bs
from typing import Dict


def get_product_data(url: str) -> Dict:
    """
    Accesses a given URL on www.ah.nl and retrieves the product's name and price.

    Args:
        url (str): URL to a given product.

    Returns:
        Dict: product name and price under "Product" and "Price" keys.
    """
    prices = []
    bonus = False

    # Fetch the page content
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    request = requests.get(url, headers=headers)

    # Check for access
    if request.status_code == 200:
        
        # Retrieve html
        html_doc = request.text
        soup = bs(html_doc, "html.parser")

        # Find div containing name and price information
        price_root_div = soup.find('div', class_=lambda classes: classes and 'Cx0SP' in classes)
        product_name_div = soup.find('div', class_=lambda classes: classes and 'c8eM5' in classes)
        
        for element in product_name_div:
            if "ahgkd" in element.get('class', [])[0]:
                product_name = element.text

        # Find child divs containing regular and sale price
        price_subdivs = price_root_div.find_all("div", recursive=False)

        # Check if the item is on sale
        if len(price_subdivs) > 1:
            bonus = True

        if bonus:

            for div in price_subdivs:
                
                # Check for old price identifier
                if "wBs7t" in div.get('class', [])[0]:
                    price = re.search(r"\d+\.\d+", div.text).group(0)
                    prices.append(float(price))

                # Check for current price identifier
                elif "Sa88q" in div.get('class', [])[0]:
                    price = re.search(r"\d+\.\d+", div.text).group(0)
                    prices.append(float(price))

        else:
            
            for div in price_subdivs:

                # Check for current price identifier
                if "Sa88q" in div.get('class', [])[0]:
                    price = re.search(r"\d+\.\d+", div.text).group(0)
                    prices.append(float(price))
            
            prices.append("NA")

    
        data_dict = {"Product": product_name, "Prices": prices}

        return data_dict
    
    elif request.status_code == 404:

        return {"Product": "NA", "Prices": ["NA", "NA"]}
    
    else:

        return None


if __name__ == "__main__":

    product_url = "https://www.ah.nl/producten/product/wi485073/nomad-heren-crew-wandelsok-maat-43-46"
    product_price = get_product_data(product_url)

    print(product_price)