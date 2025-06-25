from google import genai
import sys
import time

class LLMSummarizer:
    """
    A client to interact with a Large Language Model (LLM) for summarization
    and affiliation confirmation, with built-in retry logic for rate limiting.
    """
    def __init__(self, config):
        """
        Initializes the LLMSummarizer with a configuration object and sets up the LLM client.
        
        Args:
            config: An instance of the Config class.
        """
        self.config = config
        self.llm_client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Private method to initialize the genai.Client.
        """
        if not self.config.GOOGLE_API_KEY or self.config.GOOGLE_API_KEY == "****":
            print("Error: LLM API Key is not set. Please set the GOOGLE_API_KEY environment variable or edit config.py.")
            sys.exit(1)
        try:
            # Preserving the exact client initialization from the original script
            self.llm_client = genai.Client(api_key=self.config.GOOGLE_API_KEY)
            # This message will now only appear once when the orchestrator is created.
            # print("LLM Client (genai.Client) initialized successfully within LLMSummarizer.")
        except Exception as e:
            print(f"Fatal error: Failed to initialize Gemini Client within LLMSummarizer: {e}")
            sys.exit(1)

    def process_text(self, paper_text, max_retries=3):
        """
        Processes a given text with the LLM to get a summary and an affiliation match decision.
        Includes retry logic for handling API rate limits (429 errors).
        
        Args:
            paper_text (str): The text extracted from a paper PDF.
            max_retries (int): The maximum number of times to retry on failure.
            
        Returns:
            tuple: A tuple containing (is_match (bool), summary (str or None)).
        """
        if not self.llm_client:
            print("[Warning] LLM client is not initialized. Skipping processing.")
            return False, None

        institutions_str = ", ".join([f'"{inst}"' for inst in self.config.TARGET_INSTITUTIONS])
        
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
        
        model_name_for_call = f"models/{self.config.MODEL_NAME}"
        print(f"Call LLM (Model: {model_name_for_call})...")

        for attempt in range(max_retries):
            try:
                response = self.llm_client.models.generate_content(
                    model=model_name_for_call,
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
                # Check if it's a rate limit error and if we can still retry
                if "429" in str(e) and attempt < max_retries - 1:
                    # Exponential backoff: wait longer after each failed attempt
                    delay = 5 * (2 ** attempt)  # 5s, 10s, 20s...
                    print(f"  -> [Info] Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    # If it's another type of error or we've run out of retries
                    print(f"[Warning] Gemini API call failed on attempt {attempt + 1}: {e}")
                    return False, None