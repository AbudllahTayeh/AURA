import logging
from typing import Optional

import wikipedia

logger = logging.getLogger(__name__)

def search_wikipedia(query: str) -> Optional[str]:
    """
    Searches Wikipedia and returns a clean summary of the topic.
    
    Args:
        query (str): The topic to search for.
        
    Returns:
        Optional[str]: The text summary, or None if not found.
    """
    logger.info(f"Executing Wikipedia search for: '{query}'")
    
    try:
        # Auto-suggests the closest matching page and limits to 5 sentences
        summary = wikipedia.summary(query, sentences=5, auto_suggest=True)
        logger.info("Successfully retrieved Wikipedia summary.")
        return summary
        
    except wikipedia.exceptions.DisambiguationError as e:
        logger.warning(f"Disambiguation error for '{query}'. Options: {e.options[:5]}")
        return f"Query is too broad. Please be more specific. Options include: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        logger.warning(f"No Wikipedia page found for '{query}'.")
        return None
    except Exception as e:
        logger.error(f"Wikipedia search failed: {str(e)}")
        return None

# --- Quick Test Block ---
if __name__ == "__main__":
    test_topic = "Artificial neural network"
    print(f"Testing Wikipedia search for: '{test_topic}'\n")
    
    wiki_summary = search_wikipedia(test_topic)
    print(wiki_summary)