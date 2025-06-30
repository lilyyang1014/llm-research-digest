import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Import our new CRUD tools and database session provider
import crud
from database import SessionLocal

# Import schemas for data validation
import schemas

# --- IMPORTANT: Import your original classes ---
# We assume these files are in the same directory.
from arxiv_client import ArxivClient
from pdf_downloader import PdfDownloader
from pdf_processor import PdfProcessor
from llm_summarizer import LLMSummarizer
from config import Config

def process_and_save_papers(date_str: str):
    """
    The main background task that orchestrates the entire workflow.
    It fetches, filters, processes, and saves papers to the database.

    Args:
        date_str (str): The target date in 'YYYYMMDD' format.
    """
    print(f"--- Starting background task for date: {date_str} ---")

    # Each background task should get its own database session.
    db: Session = SessionLocal()

    try:
        # --- Instantiate your original components ---
        # Note: We create a new Config object here. Since it's now static,
        # it doesn't matter if it's created multiple times.
        config_instance = Config()
        
        # We need to make a small temporary adjustment to your original classes
        # to accept the date parameter instead of calculating it internally.
        
        # --- Step 1: arXiv Search and Keyword Filtering ---
        arxiv_client = ArxivClient(config_instance)
        # We'll need to slightly modify ArxivClient to accept a date.
        # For now, let's assume a hypothetical `search_by_date` method.
        # This is a placeholder for now, we will fix it in the next step.
        print("Step 1: Searching arXiv...")
        target_date_start = f"{date_str}000000"
        target_date_end = f"{date_str}235959"
        
        # This is a mock implementation. We will modify the actual class later.
        initial_papers = arxiv_client.search_and_filter_papers(
            date_start_str=target_date_start,
            date_end_str=target_date_end
        )
        if not initial_papers:
            print("No papers found matching keywords on arXiv. Task finished.")
            return

        print(f"Found {len(initial_papers)} initial papers.")

        # --- Instantiate other components ---
        downloader = PdfDownloader(config_instance)
        pdf_processor = PdfProcessor(config_instance)
        summarizer = LLMSummarizer(config_instance)
        
        # We need a temporary download directory for PDFs
        os.makedirs(Config.TEMP_DOWNLOAD_DIR, exist_ok=True)

        # --- Step 2 & 3: Download, Process, and Save each paper ---
        print("\nStep 2 & 3: Processing each paper individually...")
        for i, paper_from_arxiv in enumerate(initial_papers):
            short_id = paper_from_arxiv.get_short_id()
            print(f"[{i+1}/{len(initial_papers)}] Processing: {short_id} - {paper_from_arxiv.title[:50]}...")

            # Check if paper already exists in DB
            if crud.get_paper_by_arxiv_id(db, arxiv_id=short_id):
                print(f"  -> Paper {short_id} already exists in the database. Skipping.")
                continue

            # Download the PDF to a temporary location
            filepath, filename = downloader.download_single_paper(paper_from_arxiv, Config.TEMP_DOWNLOAD_DIR)
            if not filepath:
                print(f"  -> Failed to download PDF for {short_id}. Skipping.")
                continue

            # Filter by affiliation from the PDF content
            # This logic needs to be extracted from your old PdfProcessor
            match_reason = pdf_processor.check_affiliation_single_pdf(filepath)
            if not match_reason:
                print(f"  -> No affiliation match found in PDF. Skipping.")
                os.remove(filepath)  # Clean up the downloaded file
                continue
            
            print(f"  -> Affiliation match found: {match_reason}")

            # Use LLM to get summary and final confirmation
            extracted_text = pdf_processor.extract_text(filepath)
            if not extracted_text:
                print("  -> Could not extract text. Skipping.")
                os.remove(filepath)
                continue

            is_match, summary = summarizer.process_text(extracted_text)
            
            # Clean up the downloaded file immediately after use
            os.remove(filepath)

            if not is_match or not summary:
                print(f"  -> LLM did not confirm match or summary failed. Skipping.")
                continue

            print(f"  -> LLM confirmed match and generated summary.")

            # --- Step 4: Save to Database using CRUD operations ---
            paper_data = schemas.PaperBase(
                arxiv_id=short_id,
                title=paper_from_arxiv.title,
                abstract=paper_from_arxiv.summary,
                publish_date=paper_from_arxiv.published.date(),
                llm_summary=summary
            )
            
            # For now, let's use the match_reason as the institution name.
            # A more robust solution would parse the name properly.
            institution_names = [match_reason.split(':')[1].strip()] if ':' in match_reason else [match_reason]

            crud.create_paper(db=db, paper=paper_data, institution_names=institution_names)
            print(f"  -> Successfully saved paper {short_id} to the database!")

    finally:
        # Always close the database session in the end
        db.close()
        print(f"--- Background task for date: {date_str} finished ---")