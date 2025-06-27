# ArXiv LLM Digest: Your AI Research Wingman!

Too many papers, too little time? I'm your automated assistant, diving into arXiv to fetch the freshest LLM research from top labs. Think of me as your AI research tasting menu – only the best!  


🌟 Features

✅ Smart Keyword Filtering: Automatically identifies LLM-related papers using predefined keywords  
✅ Top Labs Only: The Cutting Edge!I focus on research from the best academic and industry minds  
✅ AI-Generated Summaries: Gemini 2.0 Flash Does the Reading!Get concise paper takeaways in a flash!  
✅ Automatic Report: Creates consolidated markdown reports of filtered papers 

🌟 Future Plan  
I am still a little baby but I'm growing and will become much more powerful. User experience enhancements are coming, such as options to select specific labs and configure the update frequency (daily, weekly, monthly). Please stay tuned!

📦 **Requirements**

✅Python 3.7+  
✅Required libraries: arxiv PyMuPDF (fitz) google-generativeai re os time shutil sys


🚀 **Installation**

Clone this repository: 
```bash
git clone https://github.com/lilyyang1014/llm-research-digest.git
cd llm-research-digest
```

Install dependencies: 
```bash
pip install arxiv pymupdf google-generativeai
```


🛠️ **Configuration & Usage**

#### 1. Configure Your Settings in `config.py`

All major settings are now located in the `config.py` file. You can easily modify:
*   **`KEYWORDS`**: The list of keywords to search for on arXiv.
*   **`TARGET_INSTITUTIONS`**: The list of top-tier labs to filter by.
*   **`API_CALL_DELAY_SECONDS`:** The pause duration between API calls.
*   ... and other settings!

The script is now set to **automatically fetch data for the previous day**

#### 2. Set Up Your Environment

**A. Set Your Google API Key (Required)**

For security, the application reads your API key from an environment variable. Open your terminal and run:

**On macOS / Linux:**
```bash
export GOOGLE_API_KEY="YOUR_REAL_API_KEY_HERE"
```
**On Windows(PowerShell):**
```bash
$env:GOOGLE_API_KEY="YOUR_REAL_API_KEY_HERE"
```
‼️ **Important:** Please keep your API key private. Do not commit it to your code or share it publicly.

**B. Set Your Output Directory (Optional)**

The script generates all output files (PDFs, reports) in a specific directory named by the date (MMDDYYYY format). You can configure this in the main LLMDigest.py file:
```python
# In LLMDigest.py
# Set to your desired absolute path for the base output folder.
# All date-stamped subfolders will be created inside this path.
# Set to None to use the current working directory as the base.
PROJECT_ROOT = '/path/to/your/output/folder'
```

**3. Run the Application**
Once everything is configured, simply execute the main script:
```bash
python3 LLMDigest.py
```


📝 **Output**


The script creates a new folder inside your configured base directory, named by the date (e.g., MMDDYYYY). This folder contains:

- All initially downloaded paper PDFs.

- A Final_Selected_Papers subdirectory with institution-matched papers.

- The final consolidated Markdown report with AI-generated summaries.  


🔒 Privacy & Ethics This tool is designed for research purposes only. 

‼️ Please keep your API key in your .env, please do not upload it to github.

🙋‍♀️ Author: Liuying Yang, Wei Li

🤝 Contributions are welcome! Please feel free to submit a Pull Request.
