import logging
from typing import Any, Dict, List

import arxiv

# Set up logging for Mohammed's monitoring dashboard
logger = logging.getLogger(__name__)

def search_arxiv(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Searches the arXiv database for academic papers and returns their metadata.
    """
    logger.info(f"Executing academic search for: '{query}'")
    
    try:
        results = []
        # Construct the default API client 
        client = arxiv.Client() 
        
        # Configure the search parameters
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        # The results method returns a generator of paper metadata 
        for paper in client.results(search):
            # Extracting author names from the arxiv.Author objects 
            author_names = [author.name for author in paper.authors]
            
            results.append({
                "title": paper.title,
                "authors": author_names,
                "url": paper.entry_id,          # URL to the abstract page 
                "pdf_url": paper.pdf_url,       # Direct URL to the PDF 
                "summary": paper.summary[:400] + "..." # Truncating summary for the LLM context window
            })
            
        logger.info(f"Successfully retrieved {len(results)} academic papers.")
        return results

    except Exception as e:
        logger.error(f"Academic search failed for query '{query}': {str(e)}")
        return []

# --- Quick Test Block ---
if __name__ == "__main__":
    test_query = "Quantum computing machine learning"
    print(f"Testing academic search for: '{test_query}'\n")
    
    academic_results = search_arxiv(test_query)
    
    for i, res in enumerate(academic_results, 1):
        print(f"Result {i}:")
        print(f"Title: {res['title']}")
        print(f"Authors: {', '.join(res['authors'])}")
        print(f"URL: {res['url']}")
        print(f"PDF URL: {res['pdf_url']}")
        print(f"Summary: {res['summary']}\n")
        print("-" * 40 + "\n")