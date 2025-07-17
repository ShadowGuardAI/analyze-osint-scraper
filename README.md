# analyze-osint-scraper
Scrapes OSINT sources (e.g., social media, forums, pastebins) for mentions of specific keywords or IOCs. Uses libraries like `requests` and `beautifulsoup4`. - Focused on Data analysis and reporting

## Install
`git clone https://github.com/ShadowGuardAI/analyze-osint-scraper`

## Usage
`./analyze-osint-scraper [params]`

## Parameters
- `-h`: Show help message and exit
- `-k`: List of keywords to search for.
- `-i`: No description provided
- `-u`: List of URLs to scrape.
- `-o`: Output CSV file path.
- `--max_pages`: Maximum number of pages to scrape per URL.  Useful for sites with pagination. Defaults to 1.

## License
Copyright (c) ShadowGuardAI
