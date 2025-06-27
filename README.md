# ArXiv LLM Digest: Your AI Research Wingman!

Too many papers, too little time? I'm your automated assistant, diving into arXiv to fetch the freshest LLM research from top labs. Think of me as your AI research tasting menu – only the best!  


🌟 Features

✅ Smart Keyword Filtering: Automatically identifies LLM-related papers using predefined keywords  
✅ Top Labs Only: The Cutting Edge!I focus on research from the best academic and industry minds  
✅ AI-Generated Summaries: Gemini 2.0 Flash Does the Reading!Get concise paper takeaways in a flash!  
✅ Automatic Report: Creates consolidated markdown reports of filtered papers 

🌟 Future Plan  
I am still a little baby but I'm growing and will become much more powerful. User experience enhancements are coming, such as options to select specific labs and configure the update frequency (daily, weekly, monthly). Please stay tuned!


🛠️ Configuration & Usage:

```python
# LLM-related keywords for initial filtering  
KEYWORDS = ['llm', 'large language model', 'language model',
            'foundation model', 'pretrained language model',
            'transformer', 'generative ai'
            ]  

# Target date range for paper search (YYYYMMDDHHMMSS format)  
TARGET_DATE_START = "20250411000000"  
TARGET_DATE_END = "20250411235959"  

# Target institutions for affiliation matching
TARGET_INSTITUTIONS = [ "Stanford", "Stanford University",
                        "Princeton University", "UC Berkeley",
                        "University of California, Berkeley",
                        "Berkeley", "CMU", "Carnegie Mellon University",
                        "Carnegie Mellon", "NVIDIA Research", "NVIDIA",
                        "Google Deepmind", "Deepmind", "Google", "OpenAI",
                        "University of Washington", "Cornell University",
                        "University of Illinois Urbana-Champaign", "UIUC",
                        "Allen Institute for AI", "AI2"
                        ]
```

📦 Requirements

✅Python 3.7+  
✅Required libraries: arxiv PyMuPDF (fitz) google-generativeai re os time shutil sys


🚀 Installation

Clone this repository: 
```bash
git clone https://github.com/lilyyang1014/llm-research-digest.git
```

Install dependencies: 
```bash
pip install arxiv pymupdf google-generativeai
```

Set up your Google API key:

```bash
GOOGLE_API_KEY=<your_api_key_here>
```

Configure your project path:

```bash
FIXED_PROJECT_PATH=<your_project_path>
```


📝 Output The script creates a folder structure with:

A base directory named by the date (MMDDYYYY format)  
All initially filtered papers in the base directory A "Final_Selected_Papers" subdirectory containing only institution-matched papers  
A consolidated markdown report with paper details and AI-generated summaries  


🔒 Privacy & Ethics This tool is designed for research purposes only. 

‼️ Please keep your API key in your .env, please do not upload it to github.

🙋‍♀️ Author: Liuying Yang, Wei Li

🤝 Contributions are welcome! Please feel free to submit a Pull Request.
