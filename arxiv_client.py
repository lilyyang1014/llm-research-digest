import arxiv

class ArxivClient:
    """
    A client to interact with the arXiv API.
    It encapsulates the logic for searching and initial filtering of papers.
    """
    def __init__(self, config):
        """
        Initializes the ArxivClient with a configuration object.
        
        Args:
            config: An instance of the Config class containing all necessary parameters.
        """
        self.config = config
        self._client = arxiv.Client()

    def search_and_filter_papers(self, max_results=None):
        """
        Searches arXiv based on parameters from the config object and filters
        by keywords in the title or abstract.
        
        Args:
            max_results (int, optional): The maximum number of results to return. Defaults to None.
            
        Returns:
            list: A list of arxiv.Result objects for papers that match the criteria.
        """
        print("\n--- Step 1: arXiv search and keyword filtering ---")
        
        query_string = f"cat:cs.* AND lastUpdatedDate:[{self.config.TARGET_DATE_START} TO {self.config.TARGET_DATE_END}]"
        print(f"Query string: {query_string}")
        
        search = arxiv.Search(
            query=query_string,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        filtered_papers = []
        total_count = 0
        filtered_count = 0
        
        print("Fetching and filtering papers based on title/abstract...")
        try:
            results_generator = self._client.results(search)
            for result in results_generator:
                total_count += 1
                title_lower = result.title.lower()
                summary_lower = result.summary.lower()
                
                # Use keywords from the config object
                if any(keyword in title_lower for keyword in self.config.KEYWORDS_LOWER) or \
                   any(keyword in summary_lower for keyword in self.config.KEYWORDS_LOWER):
                    filtered_count += 1
                    filtered_papers.append(result)
            
            print("-" * 30)
            print(f"Date {self.config.TARGET_DATE_START[:8]}:")
            print(f"Found {filtered_count} CS papers containing the specified keywords in title/abstract.")
            print(f"Found a total of {total_count} CS papers for the day.")
            print("-" * 30)
            
            return filtered_papers
            
        except Exception as e:
            print(f"Error: An error occurred during arXiv query or filtering: {e}")
            return []