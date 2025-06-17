import os
import arxiv
import time
import fitz  # PyMuPDF
import re
import shutil
from google import genai
import sys 

KEYWORDS = ['llm', 'large language model', 'language model', 'foundation model','pretrained language model', 
            'transformer', 'generative ai']
KEYWORDS_LOWER = [k.lower() for k in KEYWORDS]
TARGET_DATE_START = "20250411000000" 
TARGET_DATE_END = "20250411235959" 

# 1. define the fixed project path
FIXED_PROJECT_PATH = '****' # PLEASE USE YOUR OWN PATH!!!!!!

# 2. extract the date part from TARGET_DATE_START
date_part = TARGET_DATE_START[:8] # result is "20240411"

# 3. format the date part to "MMDDYYYY"
year = date_part[:4]    # "2025"
month = date_part[4:6]  # "04"
day = date_part[6:8]    # "11"
formatted_date_folder_name = f"{month}{day}{year}" # result is "04112025"

# 4. make a new BASE_DOWNLOAD_DIR using the formatted date
BASE_DOWNLOAD_DIR = os.path.join(FIXED_PROJECT_PATH, formatted_date_folder_name)

# 5. make a new FINAL_FILTERED_DIR using the formatted date
FINAL_SUBDIR_NAME = 'Final_Selected_Papers'
FINAL_FILTERED_DIR = os.path.join(BASE_DOWNLOAD_DIR, FINAL_SUBDIR_NAME)

TARGET_INSTITUTIONS = [
    "Stanford", "Stanford University", "Princeton University", "UC Berkeley", "University of California, Berkeley", 
    "Berkeley", "CMU", "Carnegie Mellon University", "Carnegie Mellon", "NVIDIA Research", "NVIDIA",
    "Google Deepmind", "Deepmind", "Google",  "OpenAI", "University of Washington", "Cornell University", 
    "University of Illinois Urbana-Champaign", "UIUC", "Allen Institute for AI", "AI2"
]
TARGET_INSTITUTIONS_LOWER = [inst.lower() for inst in TARGET_INSTITUTIONS]
TARGET_DOMAINS = [
    'stanford.edu', 'berkeley.edu', 'cs.cmu.edu', 'mit.edu', 'csail.mit.edu', 'uw.edu', 'cs.washington.edu', 'cornell.edu',
    'google.com', 'openai.com', 'cs.princeton.edu', 'illinois.edu', 'uiuc.edu', 'gatech.edu','nvidia.com', 'allenai.org'
]
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
HEADER_RATIO = 0.40

# LLM API Key
GOOGLE_API_KEY = "****" # PLEASE USE YOUR OWN KEY!!!!!!
MODEL_NAME = "gemini-2.0-flash"
CONSOLIDATED_MD_FILENAME = "consolidated_papers_summary3.md"

def search_and_filter_arxiv(keywords_lower, start_date, end_date, max_results=None):
    print("\n--- Step 1: arXiv search and keyword filtering ---")
    query_string = f"cat:cs.* AND lastUpdatedDate:[{start_date} TO {end_date}]"
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
    client = arxiv.Client()
    print("Fetching and filtering papers based on title/abstract...")
    try:
        results_generator = client.results(search)
        for result in results_generator:
            total_count += 1
            title_lower = result.title.lower()
            summary_lower = result.summary.lower()
            if any(keyword in title_lower for keyword in keywords_lower) or \
               any(keyword in summary_lower for keyword in keywords_lower):
                filtered_count += 1
                filtered_papers.append(result)
        print("-" * 30)
        print(f"Date {start_date[:8]}:")
        print(f"Found {filtered_count} CS papers containing the specified keywords in title/abstract.")
        print(f"Found a totle of {total_count} CS papers for the day.")
        print("-" * 30)
        return filtered_papers
    except Exception as e:
        print(f"Error: An error occurred during arXiv query on filtering: {e}")
        return []

def download_filtered_papers(papers_to_download, download_dir):
    print(f"\n--- Step 2: Downloading filtered papers PDFs (with validation) ---")
    print(f"Target download directory: {download_dir}")

    # make sure the download directory exists
    try:
        os.makedirs(download_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create download directory '{download_dir}': {e}")
        return (0, len(papers_to_download)) # cannot create directory, return 0 success

    download_count = 0
    total_to_download = len(papers_to_download)
    min_pdf_size_kb = 10 # define minimum PDF size in KB

    if total_to_download == 0:
        print("No papers to download.")
        return (0, 0)

    print(f"Starting to download PDF files for {total_to_download} papers...")

    for i, paper in enumerate(papers_to_download):
        download_successful = False 
        filepath = None 
        short_id = "N/A" 
        try:
            short_id = paper.get_short_id()
            ## Clean the short_id for filename
            clean_id = short_id.replace('/', '_').replace(':', '_')
            filename = f"{clean_id}.pdf"
            filepath = os.path.join(download_dir, filename)

            print(f"[{i+1}/{total_to_download}] Attempting to download: {short_id} - {paper.title[:60]}...")

            if os.path.exists(filepath):
                # if the file already exists, check its size
                try:
                    file_size = os.path.getsize(filepath)
                    if file_size >= min_pdf_size_kb * 1024:
                        print(f"  File alreayd exists and size isreasonable ({file_size / 1024:.1f} KB), skipping download: {filename}")
                        download_successful = True # mark as successful
                    else:
                        print(f"  File already exists but size is abnormal ({file_size / 1024:.1f} KB), attempting to redownload...")
                except OSError as size_error:
                    print(f"  Unable to get size of existing file, attempting to redownload... Error: {size_error}")

            # execute download only if the file does not exist or its size is abnormal
            if not download_successful: # only download if not already successful
                try:
                    # Call the download_pdf method, specifying the save directory and filename
                    paper.download_pdf(dirpath=download_dir, filename=filename)

                    # Check if the file was downloaded successfully
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        if file_size >= min_pdf_size_kb * 1024:
                            download_successful = True
                            print(f"Download successful, file size: {file_size / 1024:.1f} KB - {filename}")
                        else:
                            print(f"[Warning]Download complete but file size is abnormal ({file_size / 1024:.1f} KB), download might be incomplete: {filename}")
                            try:
                                os.remove(filepath) # try to remove the abnormal file
                                print(f"Deleted file with abnormal size: {filename}")
                            except OSError as remove_error:
                                print(f"Error deleting file with abnormal size: {remove_error}")
                    else:
                        print(f"[Error] Download reported as complete but file not found: {filename}")

                except Exception as download_error:
                    print(f"An error occurred during download: {short_id} - Error: {download_error}")
                    # if the download fails, check if a file was created
                    if filepath and os.path.exists(filepath):
                         try:
                             file_size = os.path.getsize(filepath)
                             if file_size < min_pdf_size_kb * 1024:
                                 print(f"Small file ({file_size / 1024:.1f} KB), found after download error, attempting to delete...")
                                 os.remove(filepath)
                                 print(f"Deleted small file resulting from download error: {filename}")
                         except OSError as check_error:
                             print(f"Error checking or deleting leftover file from download error: {check_error}")

            # Check if the download was successful
            if download_successful:
                download_count += 1

            print("Pause 3.5 seconds...") 
            time.sleep(3.5)

        except Exception as paper_error:
             # capture errors when processing the paper object
             print(f"Error processing paper metadata (ID: {short_id}, possible reason: {paper_error}), skipping download for this paper.")

    print("\n--- Download summary ---")
    print(f"Attempted to download: {total_to_download} papers")
    print(f"Successfully downloaded & validation(or existed with valid size): {download_count} papers")
    print(f"Failed downloads or validation failed: {total_to_download - download_count} papers")
    print(f"PDF files saved in: {download_dir}")
    print("----------------")
    return download_count, total_to_download

def filter_pdfs_by_affiliation(papers_to_check, pdf_source_dir, output_dir, target_institutions_lower, target_domains, header_ratio):
    
    print(f"\n--- Step 3: Filtering based on PDF content(Institution/Email) ---")
    print(f"Checking PDFs in source directory '{pdf_source_dir}', passing matching file information, and copying files to '{output_dir}'") 

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create output directory'{output_dir}': {e}")
        return []

    final_selected_papers_with_reason = []
    processed_count = 0
    potential_errors = 0
    total_to_check = len(papers_to_check)

    if not os.path.isdir(pdf_source_dir):
        print(f"Error: PDF source directory'{pdf_source_dir}' does not exist.")
        return []
    if total_to_check == 0:
        print("No papers to check.")
        return []

    print(f"Reading and filtering the first page of {total_to_check} corresponding paper PDFs...")

    for i, paper in enumerate(papers_to_check):
        processed_count += 1
        try:
            short_id = paper.get_short_id()
            clean_id = short_id.replace('/', '_').replace(':', '_')
            filename = f"{clean_id}.pdf"
            filepath = os.path.join(pdf_source_dir, filename)

            print(f"[{processed_count}/{total_to_check}] Processing: {filename} (Paper: {paper.title[:40]}...)")

            if not os.path.isfile(filepath):
                print(f"Warning: PDF file '{filename}' not found, skipping.")
                potential_errors += 1
                continue

            match_found = False
            match_reason = "N/A"
            doc = None

            try:
                doc = fitz.open(filepath)
                if doc.page_count > 0:
                    page = doc.load_page(0)
                    page_height = page.rect.height
                    header_limit_y = page_height * header_ratio

                    full_page_text = page.get_text()
                    emails = re.findall(EMAIL_REGEX, full_page_text)
                    if emails:
                        for email in emails:
                            try:
                                domain = email.split('@')[1].lower()
                                if any(target_domain in domain for target_domain in target_domains):
                                    match_found = True
                                    match_reason = f"Email: {email}"
                                    break
                            except IndexError:
                                continue

                    if not match_found:
                        blocks = page.get_text("blocks")
                        for block in blocks:
                            x0, y0, x1, y1, block_text, block_no, block_type = block
                            if y1 < header_limit_y:
                                block_text_lower = block_text.lower()
                                for institution in target_institutions_lower:
                                    if institution in block_text_lower:
                                        match_found = True
                                        match_reason = f"Keyword: {institution}"
                                        break
                                if match_found:
                                    break

                    doc.close()

                else:
                    print(f"Warning: PDF '{filename}' has no papes.")
                    if doc: doc.close()

                if match_found:
                    print(f"Match found: {match_reason}")
                    final_selected_papers_with_reason.append((paper, match_reason))

                    final_filepath = os.path.join(output_dir, filename)
                    if not os.path.exists(final_filepath):
                        try:
                            shutil.copy2(filepath, final_filepath)
                            print(f"Copied to'{os.path.basename(output_dir)}'")
                        except Exception as copy_error:
                             print(f"Error copying file: {copy_error}")
                             potential_errors += 1
                    else:
                        print(f"File '{filename}' already exists in the output directory, skipping copy.")

                else:
                     print("No priority match found (email domain or header keyword).")

            except Exception as e:
                potential_errors += 1
                print(f"Error processing PDF'{filename}': {e}")
                if doc:
                    try: doc.close()
                    except: pass
        except Exception as outer_e:
            potential_errors += 1
            print(f"Error processing paper object information(skipping): {outer_e}")

    print("\n--- PDF Content Filtering Summary ---")
    print(f"Total corresponding paper PDF files checked {processed_count}.")
    print(f"Number of papers selected based on content {len(final_selected_papers_with_reason)}")
    ## print(f"Number of errors/warnings encountered during filtering: {potential_errors}")
    print("-----------------------------")
    return final_selected_papers_with_reason

def extract_text_from_pdf(pdf_path, max_pages=3):
    try:
        doc = fitz.open(pdf_path)
        num_pages_to_read = min(doc.page_count, max_pages)
        if num_pages_to_read == 0:
             print(f"[Warning] PDF '{os.path.basename(pdf_path)}'has no readable pages.")
             doc.close()
             return None
        text = "".join(doc.load_page(i).get_text("text") for i in range(num_pages_to_read))
        doc.close()
        cleaned_text = "\n".join([line for line in text.splitlines() if line.strip()])
        return cleaned_text[:4000] # 保留用户限制
    except Exception as e:
        print(f"[Warning] Failed to extract text from {os.path.basename(pdf_path)}: {e}")
        return None

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

def generate_consolidated_markdown(summary_data, output_filepath, target_institutions_list):
    
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
            # f.write(f"PDFs Processed from:** `{os.path.dirname(output_filepath)}`\n\n")
            f.write("---\n\n")

            for index, (paper, reason, summary) in enumerate(summary_data):
                try:
                    title = paper.title.strip().replace('\n', ' ')
                    authors = ", ".join(author.name for author in paper.authors)
                    affiliation_evidence = reason.strip()

                    f.write(f"{index + 1}. {title}\n\n")
                    f.write(f"Authors: {authors}\n\n")
                    f.write(f"Affiliation Evidence: {affiliation_evidence}\n\n")
                    f.write(f"Summary (Gemini-2-flash Generated):\n{summary}\n\n")
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

    # --- Initialize LLM Client ---
    llm_client = None
    if not GOOGLE_API_KEY:
        print("Error: Please set LLM Key")
        sys.exit(1)
    try:
        llm_client = genai.Client(api_key=GOOGLE_API_KEY)
        print(f"LLM Client (genai.Client)initialized successfully.")
    except Exception as e:
        print(f"Fatal error: Failed to initialize Gemini Client: {e}")
        sys.exit(1)

    # --- Step 1: arXiv Search and Keyword Filtering ---
    filtered_arxiv_papers = search_and_filter_arxiv(
        KEYWORDS_LOWER, TARGET_DATE_START, TARGET_DATE_END
    )

    # --- Step2: Download Filtered Paper PDFs ---
    downloaded_count = 0
    if filtered_arxiv_papers:
        downloaded_count, _ = download_filtered_papers(filtered_arxiv_papers, BASE_DOWNLOAD_DIR)
    else:
        print("\nNo papers found in Step 1, skipping download.")

    # --- Step 3: Secondary Filtering Based on PDF Content (Institution/Email) ---
    final_papers_with_reason = []
    if filtered_arxiv_papers and os.path.isdir(BASE_DOWNLOAD_DIR):
         final_papers_with_reason = filter_pdfs_by_affiliation(
            filtered_arxiv_papers,
            BASE_DOWNLOAD_DIR,      
            FINAL_FILTERED_DIR,      
            TARGET_INSTITUTIONS_LOWER,
            TARGET_DOMAINS,
            HEADER_RATIO
        )
    else:
        print(f"\nStep 1 found no papers or source PDF directory '{BASE_DOWNLOAD_DIR}' does not exist, skipping secondary filtering.") 

    # --- Step 4: Use LLM to Extract Summaries and Re-confirm Institution ---
    matched_papers_summaries = []
    llm_processed_count = 0
    llm_matches_found = 0
    if final_papers_with_reason:
        print(f"\n--- Steo 4: Processing {len(final_papers_with_reason)} selected papers with LLM ---")
        print(f"Reading files from directory'{FINAL_FILTERED_DIR}'")

        for i, (paper, reason) in enumerate(final_papers_with_reason):
            try:
                short_id = paper.get_short_id()
                clean_id = short_id.replace('/', '_').replace(':', '_')
                filename = f"{clean_id}.pdf"
                pdf_path = os.path.join(FINAL_FILTERED_DIR, filename)

                print(f"[{i+1}/{len(final_papers_with_reason)}] LLM Processing: {filename} ...") 
                llm_processed_count += 1

                if not os.path.isfile(pdf_path):
                    print(f"Warning: PDF file '{filename}' not found in final directory, skpping LLM processing.")
                    continue

                extracted_text = extract_text_from_pdf(pdf_path)
                if not extracted_text:
                    print("Could not extract text, skipping LLM processing.") 
                    continue

                # --- Note: Using global variable MODEL_Name for model name ---
                llm_model_name_for_call = f"models/{MODEL_NAME}"
                print(f"Call LLM (Model: {llm_model_name_for_call})...") 
                is_match, summary = process_paper_with_gemini( 
                    llm_client,
                    llm_model_name_for_call,
                    extracted_text,
                    TARGET_INSTITUTIONS
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
    markdown_output_path = os.path.join(FINAL_FILTERED_DIR, CONSOLIDATED_MD_FILENAME)
    generate_consolidated_markdown(matched_papers_summaries, markdown_output_path, TARGET_INSTITUTIONS)

    print("\n=== Process finished ===")