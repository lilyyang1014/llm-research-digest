import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PdfDownloader:
    """
    Handles the downloading of PDF files for a list of arXiv papers.
    It includes validation logic based on file size.
    """
    def __init__(self, config):
        """
        Initializes the PdfDownloader with a configuration object.
        
        Args:
            config: An instance of the Config class.
        """
        self.config = config
        self.download_dir = self.config.BASE_DOWNLOAD_DIR
        self.min_pdf_size_kb = self.config.MIN_PDF_SIZE_KB

    def download_papers(self, papers_to_download):
        """
        Downloads PDFs for the given list of papers.
        
        Args:
            papers_to_download (list): A list of arxiv.Result objects.
            
        Returns:
            tuple: A tuple containing (number_of_successful_downloads, total_papers_to_download).
        """
        print(f"\n--- Step 2: Downloading filtered papers PDFs (with validation) ---")
        print(f"Target download directory: {self.download_dir}")

        try:
            os.makedirs(self.download_dir, exist_ok=True)
        except OSError as e:
            print(f"Error: Failed to create download directory '{self.download_dir}': {e}")
            return (0, len(papers_to_download))

        download_count = 0
        total_to_download = len(papers_to_download)

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
                clean_id = short_id.replace('/', '_').replace(':', '_')
                filename = f"{clean_id}.pdf"
                filepath = os.path.join(self.download_dir, filename)

                print(f"[{i+1}/{total_to_download}] Attempting to download: {short_id} - {paper.title[:60]}...")

                if os.path.exists(filepath):
                    try:
                        file_size = os.path.getsize(filepath)
                        if file_size >= self.min_pdf_size_kb * 1024:
                            print(f"  File already exists and size is reasonable ({file_size / 1024:.1f} KB), skipping download: {filename}")
                            download_successful = True
                        else:
                            print(f"  File already exists but size is abnormal ({file_size / 1024:.1f} KB), attempting to redownload...")
                    except OSError as size_error:
                        print(f"  Unable to get size of existing file, attempting to redownload... Error: {size_error}")

                if not download_successful:
                    try:
                        paper.download_pdf(dirpath=self.download_dir, filename=filename, download_domain='arxiv.org')
                        if os.path.exists(filepath):
                            file_size = os.path.getsize(filepath)
                            if file_size >= self.min_pdf_size_kb * 1024:
                                download_successful = True
                                print(f"Download successful, file size: {file_size / 1024:.1f} KB - {filename}")
                            else:
                                print(f"[Warning] Download complete but file size is abnormal ({file_size / 1024:.1f} KB), download might be incomplete: {filename}")
                                try:
                                    os.remove(filepath)
                                    print(f"Deleted file with abnormal size: {filename}")
                                except OSError as remove_error:
                                    print(f"Error deleting file with abnormal size: {remove_error}")
                        else:
                            print(f"[Error] Download reported as complete but file not found: {filename}")
                    except Exception as download_error:
                        print(f"An error occurred during download: {short_id} - Error: {download_error}")
                        if filepath and os.path.exists(filepath):
                             try:
                                 file_size = os.path.getsize(filepath)
                                 if file_size < self.min_pdf_size_kb * 1024:
                                     print(f"Small file ({file_size / 1024:.1f} KB), found after download error, attempting to delete...")
                                     os.remove(filepath)
                                     print(f"Deleted small file resulting from download error: {filename}")
                             except OSError as check_error:
                                 print(f"Error checking or deleting leftover file from download error: {check_error}")

                if download_successful:
                    download_count += 1

                print("Pause 3.5 seconds...") 
                time.sleep(3.5)
            except Exception as paper_error:
                 print(f"Error processing paper metadata (ID: {short_id}, possible reason: {paper_error}), skipping download for this paper.")

        print("\n--- Download summary ---")
        print(f"Attempted to download: {total_to_download} papers")
        print(f"Successfully downloaded & validation (or existed with valid size): {download_count} papers")
        print(f"Failed downloads or validation failed: {total_to_download - download_count} papers")
        print(f"PDF files saved in: {self.download_dir}")
        print("----------------")
        return download_count, total_to_download