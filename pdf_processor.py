import os
import fitz  # PyMuPDF
import re
from typing import Optional

class PdfProcessor:
    """
    Processes a single PDF file to check for affiliation and extract text.
    """
    def __init__(self, config):
        """
        Initializes the PdfProcessor with a configuration object.
        """
        self.config = config

    def check_affiliation_single_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Checks the first page of a single PDF for target institutions or email domains.

        Args:
            pdf_path (str): The full path to the PDF file.

        Returns:
            A string with the match reason if found, otherwise None.
        """
        if not os.path.isfile(pdf_path):
            return None

        doc = None
        try:
            doc = fitz.open(pdf_path)
            if doc.page_count == 0:
                return None
            
            page = doc.load_page(0)
            
            # 1. Check for matching email domains first (more reliable)
            full_page_text = page.get_text("text")
            emails = re.findall(self.config.EMAIL_REGEX, full_page_text)
            for email in emails:
                try:
                    domain = email.split('@')[1].lower()
                    if any(target_domain in domain for target_domain in self.config.TARGET_DOMAINS):
                        # Find the actual institution name from the email domain if possible
                        matched_inst = next((inst for inst in self.config.TARGET_INSTITUTIONS if inst.lower() in domain or domain in inst.lower()), domain)
                        return f"Email Domain Match: {matched_inst}"
                except IndexError:
                    continue

            # 2. If no email match, check for keywords in the header
            header_limit_y = page.rect.height * self.config.HEADER_RATIO
            blocks = page.get_text("blocks")
            for block in blocks:
                # y1 is the bottom coordinate of the text block
                if block[3] < header_limit_y:
                    block_text_lower = block[4].lower()
                    for institution in self.config.TARGET_INSTITUTIONS_LOWER:
                        if institution in block_text_lower:
                            # Find the properly cased institution name to return
                            original_case_inst = self.config.TARGET_INSTITUTIONS[self.config.TARGET_INSTITUTIONS_LOWER.index(institution)]
                            return f"Header Keyword Match: {original_case_inst}"
                            
            return None  # No match found

        except Exception as e:
            print(f"  -> [Error] Could not process PDF {os.path.basename(pdf_path)}: {e}")
            return None
        finally:
            if doc:
                doc.close()

    def extract_text(self, pdf_path: str, max_pages: int = 3) -> Optional[str]:
        """
        Utility method to extract text from the first few pages of a PDF.
        (This method is largely unchanged but kept for its utility).
        """
        if not os.path.isfile(pdf_path):
            return None
        try:
            doc = fitz.open(pdf_path)
            num_pages_to_read = min(doc.page_count, max_pages)
            if num_pages_to_read == 0:
                doc.close()
                return None
            
            text = "".join(doc.load_page(i).get_text("text") for i in range(num_pages_to_read))
            doc.close()
            
            # A simple way to clean up excessive newlines
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', text).strip()
            # Limit text length for LLM processing
            return cleaned_text[:8000] 
        except Exception as e:
            print(f"  -> [Warning] Failed to extract text from {os.path.basename(pdf_path)}: {e}")
            return None