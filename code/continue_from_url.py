"""
This script runs identical to main.py, but takes a starting URL and only writes the csv
from this URL on and without writing headers. THis can be used in case of errors or crashes
during scraping in the main function.
"""

import csv
import os
import xml.etree.ElementTree as ET
from datetime import date
from tqdm import tqdm
from scraping_functions import get_product_data


# Retrieve current day/time for data logging
current_date = str(date.today())

starting_url = "https://www.ah.nl/producten/product/wi471359/marhaba-kalkoenrollade"

url_collection = []

# Retrieve data path
working_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(working_dir)
product_xml_path = os.path.join(project_root, "data", "product_URLs.xml")

# Load xml file containing product urls
xml_tree = ET.parse(product_xml_path)
xml_root = xml_tree.getroot()
xml_namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

# Path to csv file to write to. Filename is in (YYYY/MM/DD)
data_path = os.path.join(project_root, "data", f"{current_date}.csv")

# Find all urls in the .xml
product_urls = xml_root.findall("ns:url", xml_namespace)
for url in product_urls:
    product_url = url.find('ns:loc', xml_namespace).text
    url_collection.append(product_url)

start_index = url_collection.index(starting_url)
url_collection = url_collection[start_index:]

# Create new csv file or append to existing file
with open(data_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Iterate over URLs in the .xml file
        for product_url in tqdm(url_collection, leave=True):

            # Due to occasional bad webpage requests, retry data retrieval until succesful
            product_data = None
            while product_data is None:
                product_data = get_product_data(product_url)

            # Parse data
            product_name = product_data["Product"]

            # Create an exception for items that do not have a price
            try:
                regular_price, sale_price = product_data["Prices"]
            except Exception as e:
                regular_price, sale_price = ("NA", "NA")
            
            nutrition_values = [value for value in product_data["Nutrition"].values()]

            row = [product_name, regular_price, sale_price] + product_data["Categories"] + nutrition_values

            # Write to csv and flush to disk to iteratively add to the csv
            writer.writerow(row)
            file.flush()
