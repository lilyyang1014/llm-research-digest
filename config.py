import os

class Config:
    """
    A centralized, static configuration class for the application.
    
    This class holds constants and settings that are not expected to change during
    the application's runtime. It has been refactored to support a long-running
    web service by removing dynamic, runtime-specific values like dates and
    generated file paths.
    """

    # --- Database Configuration ---
    # Use environment variables for production. Provides a default for easy local development.
    # For local testing, this will create a 'papers.db' file in your project directory.
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./papers.db" 
        # Example for PostgreSQL: "postgresql://user:password@localhost/arxiv_db"
    )

    # --- Search & Filtering Constants ---
    KEYWORDS = [
        'llm', 'large language model', 'language model', 'foundation model',
        'pretrained language model', 'transformer', 'generative ai'
    ]
    KEYWORDS_LOWER = [k.lower() for k in KEYWORDS]

    TARGET_INSTITUTIONS = [
        "Stanford", "Stanford University", "Princeton University", "UC Berkeley", 
        "University of California, Berkeley", "Berkeley", "CMU", "Carnegie Mellon University", 
        "Carnegie Mellon", "NVIDIA Research", "NVIDIA", "Google Deepmind", "Deepmind", 
        "Google",  "OpenAI", "University of Washington", "Cornell University",
        "University of Illinois Urbana-Champaign", "UIUC", "Allen Institute for AI", "AI2"
    ]
    TARGET_INSTITUTIONS_LOWER = [inst.lower() for inst in TARGET_INSTITUTIONS]
    
    TARGET_DOMAINS = [
        'stanford.edu', 'berkeley.edu', 'cs.cmu.edu', 'mit.edu', 'csail.mit.edu', 
        'uw.edu', 'cs.washington.edu', 'cornell.edu', 'google.com', 'openai.com', 
        'cs.princeton.edu', 'illinois.edu', 'uiuc.edu', 'gatech.edu','nvidia.com', 
        'allenai.org'
    ]

    # --- PDF Processing Constants ---
    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    HEADER_RATIO = 0.40  # Percentage of the page height to consider as header for affiliation search
    MIN_PDF_SIZE_KB = 10

    # --- LLM API Configuration ---
    # It's highly recommended to set your GOOGLE_API_KEY as an environment variable.
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("[WARNING] GOOGLE_API_KEY environment variable is not set. LLM features will fail.")
    
    MODEL_NAME = "gemini-1.5-flash" # Updated to a more recent model
    API_CALL_DELAY_SECONDS = 5 # Delay between consecutive API calls to avoid rate limiting

    # --- Path Configuration (Simplified for Service) ---
    # Get the absolute path of the project's root directory.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # A single, fixed directory for temporary PDF downloads.
    # Your application should ensure this directory exists.
    TEMP_DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'temp_downloads')
