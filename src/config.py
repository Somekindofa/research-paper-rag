"""
Configuration loader for Research RAG System.
Loads settings from YAML and environment variables.
"""
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"


def load_yaml_config(filename: str) -> dict[str, Any]:
    """Load a YAML configuration file."""
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_settings() -> dict[str, Any]:
    """Load and merge settings from YAML and environment variables."""
    settings = load_yaml_config("settings.yaml")
    
    # Override with environment variables if set
    if os.getenv("JAN_BASE_URL"):
        settings["jan"]["base_url"] = os.getenv("JAN_BASE_URL")
    
    if os.getenv("JAN_API_KEY"):
        settings["jan"]["api_key"] = os.getenv("JAN_API_KEY")
    
    if os.getenv("PDF_FOLDER_PATH"):
        settings["pdf"]["folder_path"] = os.getenv("PDF_FOLDER_PATH")
    
    if os.getenv("EMBEDDING_DEVICE"):
        settings["embeddings"]["device"] = os.getenv("EMBEDDING_DEVICE")
    
    if os.getenv("CHROMA_PERSIST_DIR"):
        settings["chroma"]["persist_directory"] = os.getenv("CHROMA_PERSIST_DIR")
    
    # Convert relative paths to absolute
    settings["chroma"]["persist_directory"] = str(
        PROJECT_ROOT / settings["chroma"]["persist_directory"]
    )
    settings["metadata"]["checksums_file"] = str(
        PROJECT_ROOT / settings["metadata"]["checksums_file"]
    )
    
    # Handle PDF folder path
    pdf_path = settings["pdf"]["folder_path"]
    if not os.path.isabs(pdf_path):
        settings["pdf"]["folder_path"] = str(PROJECT_ROOT / pdf_path)
    
    return settings


def get_prompts() -> dict[str, Any]:
    """Load prompt templates."""
    return load_yaml_config("prompts.yaml")


# Global settings instance (lazy loaded)
_settings = None
_prompts = None


def settings() -> dict[str, Any]:
    """Get cached settings."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def prompts() -> dict[str, Any]:
    """Get cached prompts."""
    global _prompts
    if _prompts is None:
        _prompts = get_prompts()
    return _prompts
