import os
import json
import csv
import re
from tqdm import tqdm
from nutrient_list import nutrition_labels
from datetime import datetime


def get_product_prices(ah_json_file):
    """Extract and return the regular and sale prices from the product JSON data.

    Args:
        ah_json_file (dict): Parsed JSON data of the product.

    Returns:
        tuple: A tuple containing the regular price and sale price as strings.
    """
    try:
        product_price_new = ah_json_file["card"]["products"][0]["price"]["now"]
    except KeyError:
        product_price_new = "NA"

    try:
        product_price_old = ah_json_file["card"]["products"][0]["price"]["was"]
    except KeyError:
        product_price_old = "NA"

    # Tested: product_price_old != "NA" and product_price_new == "NA" never occurs
    if product_price_old == "NA" and product_price_new != "NA":
        price_regular = product_price_new
        price_sale = "NA"
    elif product_price_old != "NA" and product_price_new != "NA":
        price_regular = product_price_old
        price_sale = product_price_new
    else:
        price_regular = "NA"
        price_sale = "NA"
    
    return price_regular, price_sale


def get_nutrition_data(ah_json_file):
    """Extract nutrition data from the product JSON and return it as a list.

    Args:
        ah_json_file (dict): Parsed JSON data of the product.

    Returns:
        list: A list of nutrition values corresponding to the defined nutrition labels.
    """
    global nutrition_labels

    def extract_energy_values(nutrient_value):
        """Extract energy values (kcal and kJ) from the nutrient value string.

        Args:
            nutrient_value (str): The nutrient value string containing energy information.

        Returns:
            tuple: A tuple containing kcal and kJ as integers.
        """
        pattern_kj_first = r"([\d.]+)\s*kJ\s*\(([\d.]+)\s*kcal\)"
        pattern_kcal_first = r"([\d.]+)\s*kcal\s*\(([\d.]+)\s*kJ\)"

        match_kj_first = re.search(pattern_kj_first, nutrient_value)
        match_kcal_first = re.search(pattern_kcal_first, nutrient_value)
        
        if match_kj_first:
            kj, kcal = match_kj_first.groups()
        elif match_kcal_first:
            kcal, kj = match_kcal_first.groups()
    
        return int(kcal), int(kj)

    try:                
        nutrition_rows = ah_json_file["card"]["meta"]["nutritions"][0]["nutrients"]
        nutrition_dict = {label: 'NA' for label in nutrition_labels}

        for nutrient in nutrition_rows:
            if nutrient["name"] != "Energie":
                if nutrient["name"] in nutrition_labels:
                    nutrition_dict[nutrient["name"]] = nutrient["value"]
            else:
                nutrition_dict["Energie (kcal)"], nutrition_dict["Energie (kJ)"] = extract_energy_values(nutrient["value"])
            
    except:
        nutrition_dict = {label: 'NA' for label in nutrition_labels}

    return list(nutrition_dict.values())


def get_categories(ah_json_file):
    """Extract product categories from the JSON data.

    Args:
        ah_json_file (dict): Parsed JSON data of the product.

    Returns:
        list: A list of categories associated with the product, filled with 'NA' if fewer than 6 categories.
    """
    categories = [category["name"] for category in ah_json_file["card"]["products"][0]["taxonomies"]]
    category_dict = {}

    # Add NA until 6 elements are in the list
    categories += ["NA"] * (6 - len(categories))

    return categories


def get_ingredients_and_allergens(ah_json_file):
    """Extract ingredients and allergen information from the JSON data.

    Args:
        ah_json_file (dict): Parsed JSON data of the product.

    Returns:
        tuple: A tuple containing ingredients, allergens, may contain allergens, and non-food ingredient statement.
    """
    # Returns Ingredients, Allergens, May contain allergens and non-food ingredient statement in that order.
    try:
        ingredients = ah_json_file["card"]["meta"]["ingredients"]
    except:
        return "NA", "NA", "NA", "NA"

    keys = ["statement", "allergens", "nonfoodIngredientStatement"]
    result_general = {key: ingredients.get(key, "NA") for key in keys}

    ingredient_list = result_general["statement"] or "NA"
    non_food_ingredient_list = result_general["nonfoodIngredientStatement"] or "NA"

    if result_general["allergens"] == "NA":
        allergens_contains = "NA"
        allergens_may_contain = "NA"
    else:
        allergens_contains = ", ".join(result_general["allergens"]["contains"]) or "NA"
        allergens_may_contain = ", ".join(result_general["allergens"]["mayContain"]) or "NA"

    return ingredient_list.replace("\n", " "), allergens_contains, allergens_may_contain, non_food_ingredient_list.replace("\n", " ")


def get_image_urls(ah_json_file):
    """Extract image URLs from the product JSON data.

    Args:
        ah_json_file (dict): Parsed JSON data of the product.

    Returns:
        list: A list of image URLs, filled with 'NA' if fewer than 3 images are found.
    """
    image_urls = ah_json_file["card"]["products"][0]["images"]
    image_resolutions = []

    for resolution in image_urls:
        image_resolutions.append(resolution["url"])
    
    # Add NA until len = 3
    image_resolutions += ["NA"] * (3 - len(image_resolutions))

    return image_resolutions


def get_csv_file_path():
    """
    Construct the file path for the CSV output based on the current date.

    The path will be stored in the "complete_datasets" directory, and the filename will 
    be formatted as "<today's date>.csv".

    Returns:
        str: The full file path of the CSV file.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')
    working_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(working_dir)
    return os.path.join(project_root, "complete_datasets", f"{today_date}.csv")


def get_json_files():
    """
    Retrieve and sort JSON files from the directory based on the current date.

    The files are assumed to be stored in a subdirectory named after the current date within
    the "json_collections" directory. The JSON files will be sorted by their numeric filename.

    Returns:
        list: A sorted list of JSON filenames in the directory.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')
    working_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(working_dir)
    jsons_path = os.path.join(project_root, "json_collections", f"product_jsons_{today_date}")

    json_files = os.listdir(jsons_path)
    return sorted(json_files, key=lambda x: int(x.split('.')[0]))


def write_csv_header(writer):
    """
    Write the header row to the CSV file.

    This function writes a fixed header that includes product attributes such as 
    product ID, name, price, categories, nutritional information, ingredients, allergens, 
    and image URLs.

    Args:
        writer (csv.writer): The CSV writer object used to write rows to the CSV file.
    """
    header = (
        ["ProductId", "ProductName", "PriceRegular", "PriceSale"] +
        ["Category1", "Category2", "Category3", "Category4", "Category5", "Category6"] +
        ["ProductUnitSize"] +
        nutrition_labels +
        ["Ingredients", "ContainedAllergens", "MayContainAllergens", "NonFoodIngredients"] +
        ["ImageLowURL", "ImageMediumURL", "ImageHighURL"]
    )
    writer.writerow(header)


def write_product_data(writer, json_data):
    """
    Extract product data from a JSON object and write it to the CSV file.

    The product data includes information such as product ID, name, prices, categories,
    unit size, nutritional information, ingredients, allergens, and image URLs.

    Args:
        writer (csv.writer): The CSV writer object used to write rows to the CSV file.
        json_data (dict): The JSON object containing product data.
    """
    product_id = json_data["card"]["products"][0]["id"]
    product_name = json_data["card"]["products"][0]["title"]
    product_price_regular, product_price_sale = get_product_prices(json_data)
    product_categories = get_categories(json_data)
    product_unit_size = json_data["card"]["products"][0]["price"].get("unitSize", "NA")
    product_nutrition = get_nutrition_data(json_data)
    product_ingredients, product_contained_allergens, product_may_contain_allergens, product_non_food_ingredients = get_ingredients_and_allergens(json_data)
    product_img_url_200px, product_img_url_400px, product_img_url_800px = get_image_urls(json_data)

    writer.writerow(
        [product_id, product_name, product_price_regular, product_price_sale] +
        product_categories +
        [product_unit_size] +
        product_nutrition +
        [product_ingredients, product_contained_allergens, product_may_contain_allergens, product_non_food_ingredients,
         product_img_url_200px, product_img_url_400px, product_img_url_800px]
    )


def write_csv_from_json_dir():
    """
    Write product data from JSON files into a CSV file.

    The function reads product information from multiple JSON files in a specific directory,
    processes each file to extract relevant product data, and writes it into a CSV file.
    The CSV file is named based on the current date and saved in the "complete_datasets" directory.
    """
    csv_file_path = get_csv_file_path()
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        write_csv_header(writer)

        json_files = get_json_files()
        for file in tqdm(json_files):
            file_path = os.path.join("json_collections", f"product_jsons_{datetime.now().strftime('%Y-%m-%d')}", file)
            
            with open(file_path, 'r') as f:
                json_data = json.load(f) 
                write_product_data(writer, json_data)


if __name__ == "__main__":
    write_csv_from_json_dir()

    # file_to_check = r"C:\Users\idris\Desktop\ah_price_project\json_collections\product_jsons_2024-10-19\582336.json"
    # with open(file_to_check, 'r') as f:
    #     json_data = json.load(f)

    #     product_id: int = json_data["card"]["products"][0]["id"]
    #     product_name: str = json_data["card"]["products"][0]["title"]
    #     product_price_regular, product_price_sale = get_product_prices(json_data)
    #     product_categories: list = get_categories(json_data)
    #     product_unit_size: str = json_data["card"]["products"][0]["price"].get("unitSize") or "NA"
    #     product_nutrition: list = get_nutrition_data(json_data)    
    #     product_ingredients, product_contained_allergens, product_may_contain_allergens, product_non_food_ingredients = get_ingredients_and_allergens(json_data)
    #     product_img_url_200px, product_img_url_400px, product_img_url_800px = get_image_urls(json_data)

    # print(product_nutrition)