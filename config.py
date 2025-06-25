import os

class Config:
    def __init__(self, fixed_project_path: str = None):
        # --- Search Keywords ---
        self.KEYWORDS = ['llm', 'large language model', 'language model', 'foundation model','pretrained language model',
                         'transformer', 'generative ai']
        self.KEYWORDS_LOWER = [k.lower() for k in self.KEYWORDS]

        # --- Date Configuration ---
        self.TARGET_DATE_START = "20250411000000"
        self.TARGET_DATE_END = "20250411235959"

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
        self.MIN_PDF_SIZE_KB = 10 # This was hardcoded in download_filtered_papers, now a config item

        # --- LLM API Configuration ---
        # **IMPORTANT:** Prioritize loading from environment variables for security.
        # If GOOGLE_API_KEY env var is not set, it will default to the placeholder "****".
        # For production use, please set GOOGLE_API_KEY environment variable.
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "****")
        if self.GOOGLE_API_KEY == "****":
            print("[WARNING] GOOGLE_API_KEY is not set via environment variable. Using hardcoded value or placeholder.")
            print("         Please set GOOGLE_API_KEY environment variable for production use.")
        self.MODEL_NAME = "gemini-2.0-flash"
        self.LLM_MODEL_NAME_FOR_CALL = f"models/{self.MODEL_NAME}" # Gemini specific format for API calls

        # --- Project Paths & Directories ---
        # Allow FIXED_PROJECT_PATH to be passed in, otherwise default to the current working directory.
        self.FIXED_PROJECT_PATH = fixed_project_path if fixed_project_path else os.getcwd()

        # Derived paths based on TARGET_DATE_START, calculated dynamically during instantiation
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