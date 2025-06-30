import os
from datetime import datetime, timedelta, timezone # <--- 1. 添加导入

class Config:
    def __init__(self, fixed_project_path: str = None):
        # --- Search Keywords ---
        self.KEYWORDS = ['llm', 'large language model', 'language model', 'foundation model','pretrained language model',
                         'transformer', 'generative ai']
        self.KEYWORDS_LOWER = [k.lower() for k in self.KEYWORDS]

        # --- Date Configuration (DYNAMIC) ---
        # Get yesterday's date in UTC, as arXiv uses UTC time.
        yesterday_utc = datetime.now(timezone.utc) - timedelta(days=1)
        date_str_for_query = yesterday_utc.strftime('%Y%m%d')

        self.TARGET_DATE_START = f"{date_str_for_query}000000"
        self.TARGET_DATE_END = f"{date_str_for_query}235959"
        # --- End of Date Configuration ---

        # --- Target Institutions and Domains ---
        self.TARGET_INSTITUTIONS = [
            "Stanford", "Stanford University", "Princeton University", "UC Berkeley", "University of California, Berkeley",
            "Berkeley", "CMU", "Carnegie Mellon University", "Carnegie Mellon", "NVIDIA Research", "NVIDIA",
            "Google Deepmind", "Deepmind", "Google",  "OpenAI", "University of Washington", "Cornell University",
            "University of Illinois Urbana-Champaign", "UIUC", "Allen Institute for AI", "AI2"
        ]
        self.TARGET_INSTITUTIONS_LOWER = [inst.lower() for inst in self.TARGET_INSTITUTIONS]
        self.TARGET_DOMAINS = [
            'stanford.edu', 'berkeley.edu', 'cs.cmu.edu', 'mit.edu', 'csail.mit.edu', 'uw.edu', 'cs.washington.edu', 'cornell.edu',
            'google.com', 'openai.com', 'cs.princeton.edu', 'illinois.edu', 'uiuc.edu', 'gatech.edu','nvidia.com', 'allenai.org'
        ]
        self.EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        self.HEADER_RATIO = 0.40
        self.MIN_PDF_SIZE_KB = 10

        # --- LLM API Configuration ---
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "****")
        if self.GOOGLE_API_KEY == "****":
            print("[WARNING] GOOGLE_API_KEY is not set via environment variable. Using hardcoded value or placeholder.")
            print("         Please set GOOGLE_API_KEY environment variable for production use.")
        self.MODEL_NAME = "gemini-2.0-flash"
        self.LLM_MODEL_NAME_FOR_CALL = f"models/{self.MODEL_NAME}"
        self.API_CALL_DELAY_SECONDS = 5

        # --- Project Paths & Directories ---
        self.FIXED_PROJECT_PATH = fixed_project_path if fixed_project_path else os.getcwd()

        # It will automatically use the new dynamic date to create the folder name.
        date_part = self.TARGET_DATE_START[:8]
        year = date_part[:4]
        month = date_part[4:6]
        day = date_part[6:8]
        self.FORMATTED_DATE_FOLDER_NAME = f"{month}{day}{year}"

        self.BASE_DOWNLOAD_DIR = os.path.join(self.FIXED_PROJECT_PATH, self.FORMATTED_DATE_FOLDER_NAME)
        self.FINAL_SUBDIR_NAME = 'Final_Selected_Papers'
        self.FINAL_FILTERED_DIR = os.path.join(self.BASE_DOWNLOAD_DIR, self.FINAL_SUBDIR_NAME)
        self.CONSOLIDATED_MD_FILENAME = "consolidated_papers_summary3.md"
        self.MARKDOWN_OUTPUT_PATH = os.path.join(self.FINAL_FILTERED_DIR, self.CONSOLIDATED_MD_FILENAME)