from header_objects import xml_headers, api_headers
from scrape_data import collect_product_jsons
from write_csv_from_jsons import write_csv_from_json_dir

def main():
    """collect all Albert Heijn product jsons and write a csv

    This function retrieves all product jsons from their sitemap xml
    and stores it into json_collections/product_jsons_yyyy-mm-dd/ as
    today's date. After data scraping, the data is written into a .csv
    file stored in complete_datasets/yyyy-mm-dd.csv as today's date
    """
    collect_product_jsons(xml_headers, api_headers, checkpoint=0)
    write_csv_from_json_dir()


if __name__ == "__main__":
    main()
