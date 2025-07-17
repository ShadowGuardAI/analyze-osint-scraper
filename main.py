import argparse
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os  # For checking file existence

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the script.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description='Scrapes OSINT sources for mentions of keywords or IOCs.')
    parser.add_argument('-k', '--keywords', nargs='+', help='List of keywords to search for.', required=False)
    parser.add_argument('-i', '--ioc_file', type=str, help='Path to a file containing IOCs (one per line).', required=False)
    parser.add_argument('-u', '--urls', nargs='+', help='List of URLs to scrape.', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output CSV file path.', default='output.csv')
    parser.add_argument('--max_pages', type=int, default=1, help='Maximum number of pages to scrape per URL.  Useful for sites with pagination. Defaults to 1.')
    return parser

def read_iocs_from_file(ioc_file_path):
    """
    Reads IOCs from a file, one IOC per line.

    Args:
        ioc_file_path (str): Path to the IOC file.

    Returns:
        list: A list of IOCs.  Returns an empty list if the file doesn't exist or is empty.
    """
    if not os.path.exists(ioc_file_path):
        logging.error(f"IOC file not found: {ioc_file_path}")
        return []

    try:
        with open(ioc_file_path, 'r') as f:
            iocs = [line.strip() for line in f if line.strip()] # Remove empty lines
        return iocs
    except Exception as e:
        logging.error(f"Error reading IOC file: {e}")
        return []

def scrape_url(url, keywords, iocs, max_pages=1):
    """
    Scrapes a URL for keywords and IOCs.

    Args:
        url (str): The URL to scrape.
        keywords (list): A list of keywords to search for.
        iocs (list): A list of IOCs to search for.
        max_pages (int):  Maximum number of pages to scrape (for paginated sites)

    Returns:
        list: A list of dictionaries, where each dictionary represents a match.
    """
    results = []
    try:
        for page_num in range(1, max_pages + 1):
            current_url = url
            if page_num > 1:
                # Attempt to handle pagination (very basic, might need customization per site)
                if "?" in url:
                    current_url = f"{url}&page={page_num}"
                else:
                    current_url = f"{url}?page={page_num}"

            logging.info(f"Scraping URL: {current_url}")
            try:
                response = requests.get(current_url, timeout=10)  # Add timeout for robustness
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching URL {current_url}: {e}")
                continue # Skip to the next URL if an error occurred

            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()

            if keywords:
                for keyword in keywords:
                    keyword = keyword.lower() # Case-insensitive search
                    if keyword in text_content.lower():
                        results.append({
                            'url': current_url,
                            'keyword': keyword,
                            'ioc': None,
                            'context': text_content[:500]  # Capture first 500 characters for context
                        })

            if iocs:
                for ioc in iocs:
                    if ioc in text_content:
                        results.append({
                            'url': current_url,
                            'keyword': None,
                            'ioc': ioc,
                            'context': text_content[:500]  # Capture first 500 characters for context
                        })
    except Exception as e:
        logging.error(f"General scraping error for URL {url}: {e}")

    return results

def save_results_to_csv(results, output_file):
    """
    Saves the scraping results to a CSV file.

    Args:
        results (list): A list of dictionaries representing the scraping results.
        output_file (str): The path to the output CSV file.
    """
    try:
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        logging.info(f"Results saved to: {output_file}")
    except Exception as e:
        logging.error(f"Error saving results to CSV: {e}")


def main():
    """
    Main function of the script.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    keywords = args.keywords if args.keywords else []
    iocs = []
    if args.ioc_file:
        iocs = read_iocs_from_file(args.ioc_file)

    all_results = []
    for url in args.urls:
        all_results.extend(scrape_url(url, keywords, iocs, args.max_pages))

    save_results_to_csv(all_results, args.output)


if __name__ == "__main__":
    main()


# Example Usage:
# 1.  python your_script_name.py -u http://example.com -k keyword1 keyword2 -o output.csv
# 2.  python your_script_name.py -u http://example.com http://example2.com -i ioc_file.txt -o output.csv
# 3.  python your_script_name.py -u http://example.com -i ioc_file.txt --max_pages 5 -o output.csv
# ioc_file.txt should contain one IOC per line.