import arxiv
from typing import List, Optional

class ArxivClient:
    """
    A client to interact with the arXiv API.
    It encapsulates the logic for searching and initial filtering of papers.
    """
    def __init__(self, config):
        """
        Initializes the ArxivClient with a configuration object.
        """
        self.config = config
        self._client = arxiv.Client()

    def search_and_filter_papers(self, date_start_str: str, date_end_str: str, max_results: Optional[int] = 200) -> List[arxiv.Result]:
        """
        Searches arXiv for a specific date range and filters by keywords.

        Args:
            date_start_str (str): The start date for the query in 'YYYYMMDDHHMMSS' format.
            date_end_str (str): The end date for the query in 'YYYYMMDDHHMMSS' format.
            max_results (int, optional): The maximum number of results to fetch from arXiv. Defaults to 200.

        Returns:
            List[arxiv.Result]: A list of paper objects that match the criteria.
        """
        print(f"\n--- Searching arXiv for date range: {date_start_str} to {date_end_str} ---")
        
        # Construct the query string dynamically based on the provided date range.
        query_string = f"cat:cs.* AND lastUpdatedDate:[{date_start_str} TO {date_end_str}]"
        
        search = arxiv.Search(
            query=query_string,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        filtered_papers = []
        try:
            results_generator = self._client.results(search)
            for result in results_generator:
                title_lower = result.title.lower()
                summary_lower = result.summary.lower()
                
                # Filter by keywords from the config
                if any(keyword in title_lower for keyword in self.config.KEYWORDS_LOWER) or \
                   any(keyword in summary_lower for keyword in self.config.KEYWORDS_LOWER):
                    filtered_papers.append(result)
            
            print(f"Found {len(filtered_papers)} CS papers matching keywords for the given date range.")
            return filtered_papers
            
        except Exception as e:
            print(f"Error: An error occurred during arXiv query: {e}")
            return []