import re
import requests
from bs4 import BeautifulSoup as bs
from typing import Dict


def extract_kcal_from_energy(energy_str):
    # Use regular expression to find patterns like 'x kcal (y kJ)' or 'y kJ (x kcal)'
    pattern = r"(\d+)\s*(?:kcal)\s*\(\s*(\d+)\s*(?:kJ)\)"  # Pattern for 'x kcal (y kJ)' format
    match = re.search(pattern, energy_str)

    if match:
        kcal = int(match.group(1))  # Extract kcal value
    else:
        # If not found, try the reverse pattern 'y kcal (x kJ)'
        pattern = r"(\d+)\s*(?:kJ)\s*\(\s*(\d+)\s*(?:kcal)\)"
        match = re.search(pattern, energy_str)
        
        if match:
            kcal = int(match.group(2))  # Extract kcal value
        else:
            kcal = "NA"  # Handle case where no kcal value is found
    
    return kcal


def get_product_data(url: str) -> Dict:
    """
    Accesses a given URL on www.ah.nl and retrieves the product's name, prices, categories and nutritional information.

    Args:
        url (str): URL to a given product.

    Returns:
        Dict: product name, prices, categories and nutrition data under "Product", "Prices", "Categories" and "Nutrition" keys.
    """
    prices = []
    bonus = False

    # Fetch the page content
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    request = requests.get(url, headers=headers)

    # Check for access
    if request.status_code == 200 and len(request.content) > 0:
        
        # Retrieve html
        html_doc = request.text
        soup = bs(html_doc, "html.parser")

        # Find div containing name and price information
        price_root_div = soup.find('div', class_=lambda classes: classes and 'Cx0SP' in classes)
        product_name_div = soup.find('div', class_=lambda classes: classes and 'c8eM5' in classes)

        if product_name_div is None or price_root_div is None:
            return None
        
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

        # Find all categories
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

        nutrition_info = {}
        nutrition_keys = ("Energie", "Koolhydraten", "waarvan suikers", "waarvan toegevoegde suikers", "Vet", "waarvan verzadigd", "waarvan onverzadigd", "Eiwitten", "Voedingsvezel", "Zout")
        table_rows = soup.find("table", class_=lambda classes: classes and 'Q3m80' in classes)

        if table_rows == None:
            nutrition_info = {"Energie": "NA", "Koolhydraten": "NA", "waarvan suikers": "NA", "waarvan toegevoegde suikers": "NA", "Vet": "NA", "waarvan verzadigd": "NA", "waarvan onverzadigd": "NA", "Eiwit": "NA", "Voedingsvezel": "NA", "Zout": "NA"}
            data_dict = {"Product": product_name, "Prices": prices, "Categories": category_collection, "Nutrition": nutrition_info}
        else:
           
            parsed_nutrition_info = {}
            table_body = table_rows.find("tbody")

            nutrition_rows = table_body.find_all("tr")

            
            for row in nutrition_rows:
                cells = row.find_all('td')
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                nutrition_info[key] = value

            limited_nutrition_info = {key: nutrition_info.get(key, "NA") for key in nutrition_keys}

            for key, value in limited_nutrition_info.items():
                if key == "Energie":
                    parsed_nutrition_info[key] = extract_kcal_from_energy(value)
                else:
                    try:
                        if "<" in value:
                            parsed_nutrition_info[key] = 0
                        else:
                            parsed_nutrition_info[key] = re.search(r'\d+(\.\d+)?', value).group()
                    except Exception as e:
                        parsed_nutrition_info[key] = "NA"

            data_dict = {"Product": product_name, "Prices": prices, "Categories": category_collection, "Nutrition": parsed_nutrition_info}

        return data_dict
    
    elif request.status_code == 404:
# "Energy", "Carbohydrates", "of which sugars", "of which added sugars", "fats", "of which saturated", "of which unsaturated", "fiber", "salt"
        return {"Product": "NA",
                "Prices": ["NA", "NA"],
                "Categories": ["NA", "NA", "NA", "NA", "NA", "NA"],
                "Nutrition": {"Energie": "NA", "Koolhydraten": "NA", "waarvan suikers": "NA", "waarvan toegevoegde suikers": "NA", "Vet": "NA", "waarvan verzadigd": "NA", "waarvan onverzadigd": "NA", "Voedingsvezel": "NA", "Zout": "NA"}}
    
    else:

        return None


if __name__ == "__main__":

    product_url = "https://www.ah.nl/producten/product/wi214659/croma-mild-met-olijfolie"
    product_price = get_product_data(product_url)

    print(product_price)