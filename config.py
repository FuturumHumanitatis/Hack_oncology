"""
Configuration file with constants, paths, and basic settings.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "synopsis" / "templates"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# PubMed API settings
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Statistical constants
DEFAULT_ALPHA = 0.05  # Significance level
DEFAULT_POWER = 0.80  # Statistical power
DEFAULT_DROPOUT_RATE = 0.15  # Expected dropout rate

# Regulatory settings
REGULATORY_BODIES = ["FDA", "EMA", "NMPA"]
GCP_COMPLIANCE = True

# Study design defaults
AVAILABLE_DESIGNS = [
    "parallel",
    "crossover",
    "factorial",
    "adaptive"
]

# PK parameter defaults
PK_PARAMETERS = [
    "Cmax",  # Maximum concentration
    "AUC",   # Area under curve
    "Tmax",  # Time to maximum concentration
    "t1/2",  # Half-life
    "CL",    # Clearance
    "Vd"     # Volume of distribution
]

# Synopsis sections
SYNOPSIS_SECTIONS = [
    "title",
    "background",
    "objectives",
    "study_design",
    "study_population",
    "treatment",
    "endpoints",
    "statistical_analysis",
    "sample_size",
    "regulatory"
]
