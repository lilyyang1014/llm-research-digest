# This is the main entry point of the application.
from workflow import WorkflowOrchestrator
import os

if __name__ == "__main__":
    # Define your project's root path here.
    # If set to None, it will default to the current working directory.
    # Example: PROJECT_ROOT = '/Users/yaofu/dev/LLM_Research_daily_digest'
    PROJECT_ROOT = '**************************************************************' # <--- IMPORTANT: SET YOUR PROJECT PATH HERE or set to None

    # 1. Create an instance of the orchestrator, passing the project path.
    orchestrator = WorkflowOrchestrator(config_path=PROJECT_ROOT)
    
    # 2. Run the entire workflow.
    orchestrator.run()
