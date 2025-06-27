import time
import os
from config import Config
from arxiv_client import ArxivClient
from pdf_downloader import PdfDownloader
from pdf_processor import PdfProcessor
from llm_summarizer import LLMSummarizer
from report_generator import ReportGenerator

class WorkflowOrchestrator:
    """
    Orchestrates the entire workflow of fetching, filtering, processing,
    and summarizing research papers.
    """
    def __init__(self, config_path=None):
        """
        Initializes the orchestrator and all its components.
        
        Args:
            config_path (str, optional): The path to the project's root directory.
                                         Passed to the Config class. Defaults to None.
        """
        print("=== Initializing Workflow Orchestrator ===")
        # 1. Initialize Config
        self.config = Config(fixed_project_path=config_path)
        
        # 2. Initialize all functional components with the config object
        self.arxiv_client = ArxivClient(self.config)
        self.downloader = PdfDownloader(self.config)
        self.pdf_processor = PdfProcessor(self.config)
        self.summarizer = LLMSummarizer(self.config)
        self.report_generator = ReportGenerator(self.config)
        
    def run(self):
        """
        Executes the entire workflow from start to finish using live data.
        """
        print("\n=== Starting paper filtering and summarization process ===")

        # --- Step 1: arXiv Search and Keyword Filtering ---
        filtered_arxiv_papers = self.arxiv_client.search_and_filter_papers()

        # --- Step 2: Download Filtered Paper PDFs ---
        if filtered_arxiv_papers:
            self.downloader.download_papers(filtered_arxiv_papers)
        else:
            print("\nNo papers found in Step 1, skipping download.")
            # If no papers are found, we can exit early.
            print("\n=== Process finished (no papers to process) ===")
            return

        # --- Step 3: Secondary Filtering Based on PDF Content (Institution/Email) ---
        final_papers_with_reason = []
        if os.path.isdir(self.config.BASE_DOWNLOAD_DIR):
            final_papers_with_reason = self.pdf_processor.filter_by_affiliation(filtered_arxiv_papers)
        else:
            print(f"\nSource PDF directory '{self.config.BASE_DOWNLOAD_DIR}' does not exist, skipping secondary filtering.") 

        # --- Step 4: Use LLM to Extract Summaries and Re-confirm Institution ---
        matched_papers_summaries = []
        if final_papers_with_reason:
            print(f"\n--- Step 4: Processing {len(final_papers_with_reason)} selected papers with LLM ---")
            print(f"Reading files from directory '{self.config.FINAL_FILTERED_DIR}'")

            for i, (paper, reason) in enumerate(final_papers_with_reason):
                try:
                    short_id = paper.get_short_id()
                    clean_id = short_id.replace('/', '_').replace(':', '_')
                    filename = f"{clean_id}.pdf"
                    pdf_path = os.path.join(self.config.FINAL_FILTERED_DIR, filename)

                    print(f"[{i+1}/{len(final_papers_with_reason)}] LLM Processing: {filename} ...") 

                    if not os.path.isfile(pdf_path):
                        print(f"  -> Warning: PDF file '{filename}' not found in final directory, skipping LLM processing.")
                        continue

                    extracted_text = self.pdf_processor.extract_text(pdf_path)
                    if not extracted_text:
                        print("  -> Could not extract text, skipping LLM processing.") 
                        continue
                    
                    is_match, summary = self.summarizer.process_text(extracted_text)
                        
                        
                    if is_match:
                        print(f"  -> LLM confirmed match")
                        if summary:
                            matched_papers_summaries.append((paper, reason, summary))
                            print(f"  -> Summary collected.") 
                        else:
                            print(f"  -> [Warning] Match confirmed, but no valid summary obtained.")
                            matched_papers_summaries.append((paper, reason, "[LLM Summary generation failed or was empty]"))
                    else:
                        print(f"  -> LLM did not confirm match")

                    if i < len(final_papers_with_reason) - 1:
                        delay = self.config.API_CALL_DELAY_SECONDS
                        print(f"Pausing for {delay} seconds...")
                        time.sleep(delay)

                except Exception as loop_error:
                     paper_id_str = f"ID: {paper.entry_id}" if paper else "Unknown Paper"
                     print(f"  -> Unexpected error during LLM step for paper {paper_id_str}: {loop_error}")
                     continue

            print("\n--- LLM Processing Summary ---")
            print(f"Files attempted for processing: {len(final_papers_with_reason)}")
            print(f"LLM confirmed matches: {len(matched_papers_summaries)}")
            print("--------------------")
        else:
            print("\nStep 3 selected no files, skipping LLM processing.") 

        # --- Step 5: Generate Markdown Summary Report ---
        self.report_generator.generate_markdown(matched_papers_summaries)

        print("\n=== Process finished ===")