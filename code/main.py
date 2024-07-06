import csv
import os
import xml.etree.ElementTree as ET
from datetime import date, datetime
from tqdm import tqdm
from scraping_functions import get_product_data


# Retrieve current day/time for data logging
current_date = str(date.today())

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

# Create new csv file or append to existing file
with open(data_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write headers and data logs
        writer.writerow(["Product", "Regular price", "Sale price"])

        # Find all urls in the .xml
        product_urls = xml_root.findall("ns:url", xml_namespace)
        
        # Iterate over URLs in the .xml file
        for url in tqdm(product_urls, leave=True):

            product_url = url.find('ns:loc', xml_namespace).text

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

            # Write to csv and flush to disk to iteratively add to the csv
            writer.writerow([product_name, regular_price, sale_price])
            file.flush()