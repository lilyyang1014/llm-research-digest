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
from llm_summarizer import LLMSummarizer

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

    # --- Step 1: arXiv Search and Keyword Filtering ---
    # Create an instance of our new client
    client = ArxivClient(config)
    # Call the method to get the papers
    filtered_arxiv_papers = client.search_and_filter_papers()

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
        print(f"\n--- Step 4: Processing {len(final_papers_with_reason)} selected papers with LLM ---")
        print(f"Reading files from directory'{config.FINAL_FILTERED_DIR}'")

        # Create an instance of our new summarizer. This will also initialize the LLM client.
        summarizer = LLMSummarizer(config)

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

                is_match, summary = summarizer.process_text(extracted_text)

                if is_match:
                    llm_matches_found += 1
                    print(f"  -> LLM confirmed match")
                    if summary:
                        matched_papers_summaries.append((paper, reason, summary))
                        print(f"  -> Summary collected.") 
                    else:
                        print(f"  -> [Warning] Match confirmed, but no valid summary obtained.")
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