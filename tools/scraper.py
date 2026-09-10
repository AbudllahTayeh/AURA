import logging
from typing import Optional

import trafilatura

# Set up logging so Mohammed's monitoring agent can track extraction failures
logger = logging.getLogger(__name__)

def scrape_url(url: str) -> Optional[str]:
    """
    Downloads and extracts clean text from a webpage URL.
    
    Args:
        url (str): The webpage URL to scrape.
        
    Returns:
        Optional[str]: The extracted text, or None if extraction fails.
    """
    logger.info(f"Attempting to scrape URL: {url}")
    
    try:
        # Step 1: Download the raw HTML
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            logger.warning(f"Failed to download URL: {url}")
            return None
            
        # Step 2: Extract the main article text
        # We set include_comments and include_tables to False to keep the data as clean as possible for RAG
        result = trafilatura.extract(
            downloaded, 
            include_comments=False, 
            include_tables=False
        )
        
        if result:
            logger.info(f"Successfully extracted {len(result)} characters from {url}")
            return result
        else:
            logger.warning(f"No meaningful text extracted from {url}")
            return None
            
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None

# --- Quick Test Block ---
if __name__ == "__main__":
    # We will test it on a standard blog post
    test_url = "https://en.wikipedia.org/wiki/Palestine"
    print(f"Testing scraper on: {test_url}\n")
    
    clean_text = scrape_url(test_url)
    
    if clean_text:
        print("Success! Here is a preview of the extracted text:\n")
        # Print the first 500 characters to verify it looks like a real article
        print(clean_text[:500] + "...\n")
        print(f"Total length: {len(clean_text)} characters.")
    else:
        print("Failed to extract text.")