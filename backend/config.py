"""
Configuration settings for the Closed-Loop Agentic Code Translation Framework.
"""
import os

# Default LLM Settings
DEFAULT_MODEL = "gemini-2.5-flash"
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# Multi-Agent Repair Settings
MAX_REPAIR_ATTEMPTS = 5
SANDBOX_TIMEOUT_SECONDS = 15


def get_api_key() -> str:
    """Retrieve Gemini API key from environment."""
    key = os.environ.get(API_KEY_ENV_VAR) or os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("[WARNING] GEMINI_API_KEY not found in environment. Please set GEMINI_API_KEY.")
    return key or ""
