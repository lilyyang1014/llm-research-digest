import os
import arxiv
import time
import fitz  # PyMuPDF
import re
import shutil
from google import genai
import sys 
from config import Config
from arxiv_client import ArxivClient
from pdf_downloader import PdfDownloader
from PdfProcessor import PdfProcessor

def process_paper_with_gemini(llm_client, model_name, paper_text, target_institutions_list):
    institutions_str = ", ".join([f'"{inst}"' for inst in target_institutions_list])
    prompt = f"""
    Analyze the following paper text:
    --- Paper Text ---
    {paper_text}
    --- End Paper Text ---

    Please complete the following tasks:
    1.  **Affiliation Check:** Does the text mention affiliations explicitly matching any of these institutions or their common variations: {institutions_str}? Respond ONLY with "MATCH" or "NO_MATCH".
    2.  **Summary:** If Task 1 is "MATCH", please provide a concise (3-5 sentences) summary in English of the paper's core idea and main contributions. If Task 1 is "NO_MATCH", omit this part.

    Output Format Requirements:
    - Strictly start with "MATCH" or "NO_MATCH".
    - If "MATCH", add a newline, then the summary content.

    Example:
    MATCH
    This paper introduces a novel method for improving efficiency in large language models by utilizing sparse attention mechanisms, demonstrating significant speedups on benchmark tasks.

    or

    NO_MATCH
    """
    try:
        response = llm_client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        response_text = response.text.strip()
        parts = response_text.split('\n', 1)
        decision = parts[0].strip().upper()

        if decision == "MATCH":
            summary = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "[LLM Summary generation failed or was empty]"
            return True, summary
        elif decision == "NO_MATCH":
            return False, None
        else:
            print(f"  -> [Warning] Unrecognized API response: {response_text[:50]}...")
            return False, None

    except Exception as e:
        print(f"[Warning] Gemini API call failed: {e}")
        return False, None

def generate_consolidated_markdown(summary_data, output_filepath, target_institutions_list, formatted_date_folder_name):
    
    print(f"\n--- Step 5: Generating Markdown Summary Report ---")
    if not summary_data:
        print("No LLM-confirmed matching papers found, skipping Markdown generation.")
        return

    markdown_title = f"{formatted_date_folder_name} Consolidated Paper Summaries"

    print(f"Writing information for {len(summary_data)} papers to file: {output_filepath} ...") 
    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(f"# {markdown_title}\n\n")
            f.write(f"Target Institutions for Filtering: Stanford University, Princeton University, UC Berkeley, CMU, University of Washington, Cornell University, UIUC, Google Deepmind, OpenAI, NVIDIA, AI2")
            f.write("\n---\n\n")

            for index, (paper, reason, summary) in enumerate(summary_data):
                try:
                    title = paper.title.strip().replace('\n', ' ')
                    authors = ", ".join(author.name for author in paper.authors)
                    affiliation_evidence = reason.strip()

                    f.write(f"{index + 1}. {title}\n\n")
                    f.write(f"Authors: {authors}\n\n")
                    f.write(f"Affiliation Evidence: {affiliation_evidence}\n\n")
                    f.write(f"Summary (Gemini-2.0-flash Generated):\n{summary}\n\n")
                    f.write("---\n\n")
                except Exception as paper_data_error:
                    paper_id_str = f"ID: {paper.entry_id}" if paper else "Unknown Paper"
                    print(f"[Error] Failed to process data for paper {paper_id_str} for Markdown generation: {paper_data_error}")
                    f.write(f"## {index + 1}. Error Processing Paper ({paper_id_str})\n\n")
                    f.write(f"Failed to write entry due to error: {paper_data_error}\n\n")
                    f.write("---\n\n")

        print(f"Markdown file'{os.path.basename(output_filepath)}' written succesffully!")
    except Exception as e:
        print(f"[Error] Failed to write Markdown file: {output_filepath} - {e}")

if __name__ == "__main__":
    print("=== Starting paper filtering and summarization process ===")

    # --- Step 0: Instantiate Config class ---
    # IMPORTANT: Replace '****$$$' with your actual project path.
    # For example: config = Config(fixed_project_path='/Users/yaofu/dev/LLM_Research_daily_digest')
    # Or, if you want it to default to the script's current working directory, use: config = Config()
    config = Config(fixed_project_path='/Users/yaofu/Desktop/NEU/Project/LLM_Research_daily_digest/Output')

    # --- Initialize LLM Client ---
    llm_client = None
    if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "****":
        print("Error: LLM API Key is not set. Please set the GOOGLE_API_KEY environment variable or edit config.py.")
        sys.exit(1)
    try:
        # This block is preserved exactly as in your original code.
        llm_client = genai.Client(api_key=config.GOOGLE_API_KEY)
        print(f"LLM Client (genai.Client)initialized successfully.")
    except Exception as e:
        print(f"Fatal error: Failed to initialize Gemini Client: {e}")
        sys.exit(1)

    # --- Step 1: arXiv Search and Keyword Filtering ---
    """ # Create an instance of our new client
    client = ArxivClient(config)
    # Call the method to get the papers
    filtered_arxiv_papers = client.search_and_filter_papers() """

    # --- Step 1: arXiv Search and Keyword Filtering (MOCKED) ---
    print("\n--- Step 1: SKIPPED (due to arXiv API instability, using mock data) ---")

    # This is a temporary measure for debugging and completing the refactoring.
    # We will manually create a dummy list to proceed with testing subsequent steps.

    class DummyAuthor:
        """A mock author class to simulate arxiv.Author."""
        def __init__(self, name):
            self.name = name

    class DummyPaper:
        """A mock paper class to simulate arxiv.Result."""
        def __init__(self, entry_id, title, summary, authors):
            self.entry_id = entry_id
            self.title = title
            self.summary = summary
            self.authors = [DummyAuthor(name) for name in authors]
    
        def get_short_id(self):
        # Simulate the get_short_id() method
            return self.entry_id.split('/')[-1]
        
        def download_pdf(self, dirpath, filename):
            # Simulate the download_pdf() method by creating a dummy file.
            # This allows subsequent steps (like PDF processing) to run without errors.
            dummy_pdf_path = os.path.join(dirpath, filename)
            # Ensure the directory exists before creating the file.
            os.makedirs(os.path.dirname(dummy_pdf_path), exist_ok=True)
            if not os.path.exists(dummy_pdf_path):
                with open(dummy_pdf_path, 'w') as f:
                    f.write("This is a dummy PDF created for testing purposes.")
            print(f"  -> (Mock Download) Created dummy file for testing: {filename}")

    # Create a list with one or more dummy papers.
    # We use a real paper ID format so that the filename generation is realistic.
    filtered_arxiv_papers = [
        DummyPaper(
            entry_id='https://arxiv.org/abs/2412.03572v2',
            title="A Test Paper about MLLM and Tools from Berkeley ",
            summary="This is a mock summary. The full text would mention Berkeley.",
            authors=["Amir Bar", "Gaoyue Zhou"]
        ),
        DummyPaper(
            entry_id='https://arxiv.org/abs/2411.08253v2',
            title="Another Test Paper from MIT",
            summary="A mock summary from someone at MIT",
            authors=["Nishanth Kumar", "William Shen"]
        )
    ]

    print(f"Mock data created with {len(filtered_arxiv_papers)} paper(s).")
    # --- End of MOCKED Step 1 ---

    # --- Step2: Download Filtered Paper PDFs ---
    downloaded_count = 0
    if filtered_arxiv_papers:
        # Create an instance of our new downloader
        downloader = PdfDownloader(config)
        # Call the method to download the papers
        downloaded_count, _ = downloader.download_papers(filtered_arxiv_papers)
    else:
        print("\nNo papers found in Step 1, skipping download.")

    # --- Step 3: Secondary Filtering Based on PDF Content (Institution/Email) ---
    final_papers_with_reason = []
    if filtered_arxiv_papers and os.path.isdir(config.BASE_DOWNLOAD_DIR):
        # Create an instance of our new processor
        pdf_processor = PdfProcessor(config)
        # Call the method to filter the papers by affiliation
        final_papers_with_reason = pdf_processor.filter_by_affiliation(filtered_arxiv_papers)
    else:
        print(f"\nStep 1 found no papers or source PDF directory '{config.BASE_DOWNLOAD_DIR}' does not exist, skipping secondary filtering.")
    

    # --- Step 4: Use LLM to Extract Summaries and Re-confirm Institution ---
    matched_papers_summaries = []
    llm_processed_count = 0
    llm_matches_found = 0
    if final_papers_with_reason:
        print(f"\n--- Steo 4: Processing {len(final_papers_with_reason)} selected papers with LLM ---")
        print(f"Reading files from directory'{config.FINAL_FILTERED_DIR}'")

        for i, (paper, reason) in enumerate(final_papers_with_reason):
            try:
                short_id = paper.get_short_id()
                clean_id = short_id.replace('/', '_').replace(':', '_')
                filename = f"{clean_id}.pdf"
                pdf_path = os.path.join(config.FINAL_FILTERED_DIR, filename)

                print(f"[{i+1}/{len(final_papers_with_reason)}] LLM Processing: {filename} ...") 
                llm_processed_count += 1

                if not os.path.isfile(pdf_path):
                    print(f"Warning: PDF file '{filename}' not found in final directory, skpping LLM processing.")
                    continue

                extracted_text = pdf_processor.extract_text(pdf_path)
                if not extracted_text:
                    print("Could not extract text, skipping LLM processing.") 
                    continue

                llm_model_name_for_call = f"models/{config.MODEL_NAME}"
                print(f"Call LLM (Model: {llm_model_name_for_call})...") 
                is_match, summary = process_paper_with_gemini( 
                    llm_client,
                    llm_model_name_for_call,
                    extracted_text,
                    config.TARGET_INSTITUTIONS
                )

                if is_match:
                    llm_matches_found += 1
                    print(f"  -> LLM confirmed match")
                    if summary:
                        matched_papers_summaries.append((paper, reason, summary))
                        print(f"Summary collected.") 
                    else:
                        print(f"[Warning] Match confirmed, but no valid summary obtained.")
                        matched_papers_summaries.append((paper, reason, "[LLM Summary generation failed or was empty]"))
                else:
                    print(f"  -> LLM did not confirm match")

                print("Pausing for 5 sec...")
                time.sleep(5)

            except Exception as loop_error:
                 paper_id_str = f"ID: {paper.entry_id}" if paper else "Unknown Paper"
                 print(f"Unexpected error during LLM step for paper {paper_id_str}: {loop_error}")
                 continue

        print("\n--- LLM Processing Summary ---")
        print(f"Files attempted for processing: {llm_processed_count}")
        print(f"LLM confirmed matches: {llm_matches_found}")
        print("--------------------")
    else:
        print("\nStep 3 selected no files or the target directory does not exist, skipping LLM processing.") 

    # --- Step 5: Generate Markdown Summary Report ---
    markdown_output_path = config.MARKDOWN_OUTPUT_PATH
    generate_consolidated_markdown(matched_papers_summaries, markdown_output_path, config.TARGET_INSTITUTIONS, config.FORMATTED_DATE_FOLDER_NAME)

    print("\n=== Process finished ===")