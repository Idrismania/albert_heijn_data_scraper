import re
import requests
from bs4 import BeautifulSoup as bs
from typing import Dict, Union


# Helper functions
def get_html_request(product_url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    request = requests.get(product_url, headers=headers)

    return request


def get_empty_product_dict() -> dict:

    empty_dict = {
            "Product": "NA",
            "Prices": ["NA", "NA"],
            "Categories": ["NA", "NA", "NA", "NA", "NA", "NA"],
            "Nutrition": {
                "Energie": "NA",
                "Koolhydraten": "NA",
                "waarvan suikers": "NA",
                "waarvan toegevoegde suikers": "NA",
                "Vet": "NA",
                "waarvan verzadigd": "NA",
                "waarvan onverzadigd": "NA",
                "Voedingsvezel": "NA",
                "Zout": "NA"
            }
        }
    
    return empty_dict


def get_price_and_product_div_from_html(html_document):

        soup = bs(html_document, "html.parser")

        # Find div containing name and price information
        price_root_div = soup.find('div', class_=lambda classes: classes and 'Cx0SP' in classes)
        product_name_div = soup.find('div', class_=lambda classes: classes and 'c8eM5' in classes)

        return price_root_div, product_name_div


def get_product_name(product_name_div) -> str:

    product_name = "NA"

    for element in product_name_div:
            if "ahgkd" in element.get('class', [])[0]:
                product_name = element.text

    return product_name


def get_product_prices(price_sub_divs, bonus=False) -> list:

    prices = []

    if bonus:

        for div in price_sub_divs:
            
            # Check for old price identifier
            if "wBs7t" in div.get('class', [])[0]:
                price = re.search(r"\d+\.\d+", div.text).group(0)
                prices.append(float(price))

            # Check for current price identifier
            elif "Sa88q" in div.get('class', [])[0]:
                price = re.search(r"\d+\.\d+", div.text).group(0)
                prices.append(float(price))

    else:
        
        for div in price_sub_divs:

            # Check for current price identifier
            if "Sa88q" in div.get('class', [])[0]:
                price = re.search(r"\d+\.\d+", div.text).group(0)
                prices.append(float(price))

        prices.append("NA")

    return prices


def get_categories_from_html(html_document) -> list:
    
    soup = bs(html_document, "html.parser")
    categories = soup.find('ol', class_=lambda classes: classes and '2d6En' in classes)

    # Save all sub categories
    category_collection = []
    for child in categories.children:
        category_collection.append(child.text)

    # Remove home and product from category
    category_collection = category_collection[2:]

    # Make the list 12 items long for csv consistency
    while len(category_collection) < 6:
        category_collection.append("NA")

    return category_collection


def get_nutrition_data(html_document) -> dict:

    
    def extract_kcal_from_energy(energy: str) -> Union[int, str]:
        """
        Use regular expression to find patterns like 'x kcal (y kJ)' or 'y kJ (x kcal)'.

        Args:
            energy (str): String containing raw kcal extraction from the Albert Heijn website.

        Returns:
            kcal (int | str): Energy in kcal as type int, or string "NA" when not available.
        """
        
        pattern = r"(\d+)\s*(?:kcal)\s*\(\s*(\d+)\s*(?:kJ)\)"  # Pattern for 'x kcal (y kJ)' format
        match = re.search(pattern, energy)

        if match:
            kcal = int(match.group(1))  # Extract kcal value
        
        else:
            # If not found, try the reverse pattern 'y kcal (x kJ)'
            pattern = r"(\d+)\s*(?:kJ)\s*\(\s*(\d+)\s*(?:kcal)\)"
            match = re.search(pattern, energy)
            
            if match:
                kcal = int(match.group(2))  # Extract kcal value
            else:
                kcal = "NA"  # Handle case where no kcal value is found
        
        return kcal


    soup = bs(html_document, "html.parser")
    table_rows = soup.find("table", class_=lambda classes: classes and 'Q3m80' in classes)
    
    if table_rows == None:
        # Return NA info if no nutrition table is found
        parsed_nutrition_info = {"Energie": "NA", "Koolhydraten": "NA", "waarvan suikers": "NA", "waarvan toegevoegde suikers": "NA", "Vet": "NA", "waarvan verzadigd": "NA", "waarvan onverzadigd": "NA", "Eiwit": "NA", "Voedingsvezel": "NA", "Zout": "NA"}

    else:

        nutrition_info = {}
        nutrition_keys = ("Energie", "Koolhydraten", "waarvan suikers", "waarvan toegevoegde suikers", "Vet", "waarvan verzadigd", "waarvan onverzadigd", "Eiwitten", "Voedingsvezel", "Zout")

        # Find nutrition table and its rows
        table_body = table_rows.find("tbody")
        nutrition_rows = table_body.find_all("tr")

        # Extract keys and values from nutrition table
        for row in nutrition_rows:
            cells = row.find_all('td')
            key = cells[0].text.strip()
            value = cells[1].text.strip()
            nutrition_info[key] = value

        limited_nutrition_info = {key: nutrition_info.get(key, "NA") for key in nutrition_keys}
        parsed_nutrition_info = {}

        # Fill parsed_nutrition_info with found information
        for key, value in limited_nutrition_info.items():
            # Save every found value into parsed nutrition, save every error as NA
            # Use separate function for kcal extraction
            if key == "Energie":
                parsed_nutrition_info[key] = extract_kcal_from_energy(value)
            else:
                # If nutrition includes < symbol, round down to 0.
                try:
                    if "<" in value:
                        parsed_nutrition_info[key] = 0
                    else:
                        parsed_nutrition_info[key] = re.search(r'\d+(\.\d+)?', value).group()
                except Exception as e:
                    parsed_nutrition_info[key] = "NA"
        
    return parsed_nutrition_info


# Main function used for scraping
def get_product_data(url: str) -> Union[Dict, None]:
    """
    Accesses a given URL on www.ah.nl and retrieves the product's name, prices, categories and nutritional information.

    Args:
        url (str): URL to a given product.

    Returns:
        Dict: product name, prices, categories and nutrition data under "Product", "Prices", "Categories" and "Nutrition" keys.
        or
        None if an error occurs
    """
    
    request = get_html_request(url)

    # Return NA for all data if the page is not found
    if request.status_code == 404:
        return get_empty_product_dict()

    # Check if the request is succesful and data is retrieved
    elif request.status_code == 200 and len(request.content) > 0:

        html_doc = request.text

        # Retrieve necessary html elements
        price_root_div, product_name_div = get_price_and_product_div_from_html(html_doc)

        # If a div cannot be found, return None so the function is restarted in main.py
        if product_name_div is None or price_root_div is None:
            return None

        # Find child divs containing regular and sale price
        price_sub_divs = price_root_div.find_all("div", recursive=False)

        bonus = True if len(price_sub_divs) > 1 else False

        # Retrieve data
        product_name = get_product_name(product_name_div)
        prices = get_product_prices(price_sub_divs, bonus)
        category_list = get_categories_from_html(html_doc)
        nutrition_data = get_nutrition_data(html_doc)


        data_dict = {"Product": product_name, "Prices": prices, "Categories": category_list, "Nutrition": nutrition_data}

        return data_dict


if __name__ == "__main__":

    # Single test case for one product
    product_url = "https://www.ah.nl/producten/product/wi61131/moet-en-chandon-champagne-nectar-imperial"
    product_data = get_product_data(product_url)

    print(product_data)