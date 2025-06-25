# pdf_processor.py

import os
import fitz  # PyMuPDF
import re
import shutil

class PdfProcessor:
    """
    Processes PDF files to extract text and filter them based on content.
    """
    def __init__(self, config):
        """
        Initializes the PdfProcessor with a configuration object.
        
        Args:
            config: An instance of the Config class.
        """
        self.config = config

    def filter_by_affiliation(self, papers_to_check):
        """
        Filters a list of papers by checking their corresponding PDF content
        for target institutions or email domains.
        
        Args:
            papers_to_check (list): A list of arxiv.Result objects.
            
        Returns:
            list: A list of tuples, where each tuple contains (paper_object, match_reason).
        """
        pdf_source_dir = self.config.BASE_DOWNLOAD_DIR
        output_dir = self.config.FINAL_FILTERED_DIR
        
        print(f"\n--- Step 3: Filtering based on PDF content (Institution/Email) ---")
        print(f"Checking PDFs in source directory '{pdf_source_dir}', copying matching files to '{output_dir}'")

        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"Error: Failed to create output directory '{output_dir}': {e}")
            return []

        final_selected_papers_with_reason = []
        processed_count = 0
        potential_errors = 0
        total_to_check = len(papers_to_check)

        if not os.path.isdir(pdf_source_dir):
            print(f"Error: PDF source directory '{pdf_source_dir}' does not exist.")
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
                        header_limit_y = page_height * self.config.HEADER_RATIO

                        full_page_text = page.get_text()
                        emails = re.findall(self.config.EMAIL_REGEX, full_page_text)
                        if emails:
                            for email in emails:
                                try:
                                    domain = email.split('@')[1].lower()
                                    if any(target_domain in domain for target_domain in self.config.TARGET_DOMAINS):
                                        match_found = True
                                        match_reason = f"Email: {email}"
                                        break
                                except IndexError:
                                    continue

                        if not match_found:
                            blocks = page.get_text("blocks")
                            for block in blocks:
                                _, y0, _, y1, block_text, _, _ = block
                                if y1 < header_limit_y:
                                    block_text_lower = block_text.lower()
                                    for institution in self.config.TARGET_INSTITUTIONS_LOWER:
                                        if institution in block_text_lower:
                                            match_found = True
                                            match_reason = f"Keyword: {institution}"
                                            break
                                    if match_found:
                                        break
                        doc.close()
                    else:
                        print(f"Warning: PDF '{filename}' has no pages.")
                        if doc: doc.close()

                    if match_found:
                        print(f"Match found: {match_reason}")
                        final_selected_papers_with_reason.append((paper, match_reason))
                        
                        final_filepath = os.path.join(output_dir, filename)
                        if not os.path.exists(final_filepath):
                            try:
                                shutil.copy2(filepath, final_filepath)
                                print(f"Copied to '{os.path.basename(output_dir)}'")
                            except Exception as copy_error:
                                print(f"Error copying file: {copy_error}")
                                potential_errors += 1
                        else:
                            print(f"File '{filename}' already exists in the output directory, skipping copy.")
                    else:
                        print("No priority match found (email domain or header keyword).")
                except Exception as e:
                    potential_errors += 1
                    print(f"Error processing PDF '{filename}': {e}")
                    if doc:
                        try: doc.close()
                        except: pass
            except Exception as outer_e:
                potential_errors += 1
                print(f"Error processing paper object information (skipping): {outer_e}")

        print("\n--- PDF Content Filtering Summary ---")
        print(f"Total corresponding paper PDF files checked: {processed_count}.")
        print(f"Number of papers selected based on content: {len(final_selected_papers_with_reason)}")
        print("-----------------------------")
        return final_selected_papers_with_reason

    def extract_text(self, pdf_path, max_pages=3):
        """
        A utility method to extract text from a PDF.
        """
        try:
            doc = fitz.open(pdf_path)
            num_pages_to_read = min(doc.page_count, max_pages)
            if num_pages_to_read == 0:
                print(f"[Warning] PDF '{os.path.basename(pdf_path)}' has no readable pages.")
                doc.close()
                return None
            text = "".join(doc.load_page(i).get_text("text") for i in range(num_pages_to_read))
            doc.close()
            cleaned_text = "\n".join([line for line in text.splitlines() if line.strip()])
            return cleaned_text[:4000]
        except Exception as e:
            print(f"[Warning] Failed to extract text from {os.path.basename(pdf_path)}: {e}")
            return None