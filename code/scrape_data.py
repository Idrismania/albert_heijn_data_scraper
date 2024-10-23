import os
import re
import xml.etree.ElementTree as ET
import requests
import json
import time
import random
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from header_objects import api_headers, xml_headers


def create_json_directory():
    """Create a directory for storing JSON files.

    This function creates a directory structure under the project root
    for storing JSON files containing product data. The directory is 
    named with the current date.

    Returns:
        str: The path to the created JSON directory.
    """
    working_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(working_dir)
    data_dir = os.path.join(project_root, "json_collections")
    os.makedirs(data_dir, exist_ok=True)

    today_date = datetime.now().strftime("%Y-%m-%d")
    json_dir = os.path.join(data_dir, f"product_jsons_{today_date}")
    os.makedirs(json_dir, exist_ok=True)

    return json_dir


def fetch_sitemap(xml_headers):
    """Fetch the sitemap XML from the specified URL.

    This function attempts to download the sitemap XML file from 
    the provided URL. It will keep retrying until a successful response
    is received.

    Args:
        xml_headers (dict): The headers to include in the request.

    Returns:
        bytes: The content of the sitemap XML.
    """
    sitemap_xml_url = "https://www.ah.nl/sitemaps/entities/products/detail.xml"
    while True:
        sitemap_response = requests.get(sitemap_xml_url, headers=xml_headers)
        if sitemap_response.status_code == 200:
            return sitemap_response.content
        print(f"XML Download unsuccessful ({sitemap_response.status_code}), retrying...")
        time.sleep(5)


def parse_product_urls(sitemap_content):
    """Parse product URLs from the sitemap XML content.

    This function extracts product URLs from the provided sitemap XML 
    content and returns the list of URLs along with the XML namespace.

    Args:
        sitemap_content (bytes): The raw XML content of the sitemap.

    Returns:
        tuple: A tuple containing a list of product URLs and the XML namespace.
    """
    xml_tree = ET.ElementTree(ET.fromstring(sitemap_content))
    xml_root = xml_tree.getroot()
    xml_namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return xml_root.findall("ns:url", xml_namespace), xml_namespace


def initialize_session(api_headers):
    """Initialize a requests session and establish cookies.

    This function creates a requests session and makes an initial request
    to establish the session and set cookies. It raises an exception 
    if the session cannot be established.

    Args:
        api_headers (dict): The headers to include in the initial request.

    Returns:
        requests.Session: A requests session object with established headers and cookies.
    
    Raises:
        Exception: If the initial request fails to establish the session.
    """
    session = requests.Session()
    session.headers.update(api_headers)

    # Optional: Make an initial request to establish a session and cookies
    initial_request = session.get("https://www.ah.nl", headers=api_headers)
    if initial_request.status_code == 200:
        print("Session established and cookies set.")
    else:
        raise Exception(f"Failed to establish session ({initial_request.status_code}).")

    return session


def fetch_product_data(session, api_search_url, headers, product_id, json_dir, max_retries=500):
    """Fetch product data from the API and save it as a JSON file, with retry logic.

    This function sends a GET request to the specified API search URL to 
    retrieve product data. It implements retry logic for handling errors 
    and saves the response data as a JSON file.

    Args:
        session (requests.Session): The session object to manage requests.
        api_search_url (str): The URL for the API endpoint to fetch product data.
        headers (dict): The headers to include in the request.
        product_id (str): The unique identifier for the product.
        json_dir (str): The directory path where the JSON file will be saved.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 500.

    Returns:
        str: The product ID if the fetch is successful, None otherwise.
    """
    for attempt in range(max_retries):
        try:
            request = session.get(api_search_url, headers=headers)

            if request.status_code == 500:
                return None
            
            elif request.status_code == 403:
                print(f"Access denied for product {product_id}. Retrying after 2 minute delay.")
                time.sleep(120)  # Wait longer after a 403 error
                continue  # Retry logic

            elif request.status_code == 404:
                print(f"Error 404 for product {product_id}.")
                return None
            
            request.raise_for_status()  
            data = request.json()
            json_file_path = os.path.join(json_dir, f"{product_id}.json")
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file)
            time.sleep(1 + random.uniform(0.25, 0.50))
            return product_id  # Return the product ID on success
        
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error fetching product {product_id} on attempt {attempt + 1}: {e}")
            time.sleep(2)  # Wait before retrying
    
    return None  # Return None if all attempts fail


def scrape_products(session, xml_namespace, json_dir, product_urls, checkpoint):
    """Scrape product data concurrently from the API.

    This function retrieves product data from the API using a thread pool
    to handle multiple requests concurrently. It processes each product URL
    and saves the resulting data to JSON files.

    Args:
        session (requests.Session): The session object to manage requests.
        xml_namespace (dict): The XML namespace used for parsing product URLs.
        json_dir (str): The directory path where the JSON files will be saved.
        product_urls (list): A list of product URL elements from the sitemap.
        checkpoint (int): The product ID threshold for skipping products.
    """
    base_api_str = r"https://www.ah.nl/zoeken/api/products/product?webshopId="
    product_id_pattern = "(?<=/wi)(\d+)"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in product_urls:
            product_url = url.find('ns:loc', xml_namespace).text
            product_id = re.search(product_id_pattern, product_url).group()
            api_search_url = base_api_str + product_id

            # SKIP PRODUCTS UP UNTIL THIS NUMBER
            if int(product_id) < checkpoint:
                continue
            
            # Submit the fetch operation to the thread pool
            futures.append(executor.submit(fetch_product_data, session, api_search_url, api_headers, product_id, json_dir))

        # Process results as they complete
        for future in tqdm(as_completed(futures), total=len(futures)):
            product_id = future.result()
            if product_id is None:
                print("Failed to fetch product data.")


def collect_product_jsons(xml_headers, api_headers, checkpoint = 0):
    """Main entry point for the product scraping script.

    This function orchestrates the scraping process by creating the JSON 
    directory, fetching the sitemap, parsing product URLs, initializing 
    the session, and scraping the product data.

    Args:
        xml_headers (dict): The headers to include in the XML request.
        api_headers (dict): The headers to include in the API requests.
    """
    json_dir = create_json_directory()
    sitemap_content = fetch_sitemap(xml_headers)
    product_urls, xml_namespace = parse_product_urls(sitemap_content)

    session = initialize_session(api_headers)

    scrape_products(session, xml_namespace, json_dir, product_urls, checkpoint)


if __name__ == "__main__":
    collect_product_jsons(xml_headers, api_headers, checkpoint=0)
